"""
玩家类：职业、属性、装备、技能、经验与升级。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core.i18n import t
from core.narrative_language import get_narrative_language
from game.constants import MAX_INVENTORY_SLOTS
from game.inventory import Inventory, InventoryItem, ItemCategory


class Profession(str, Enum):
    """四种职业，影响初始属性与升级成长。"""

    WARRIOR = "战士"
    MAGE = "法师"
    ROGUE = "盗贼"
    BARD = "吟游诗人"


# 每级所需经验（简单曲线）
def xp_for_next_level(level: int) -> int:
    return 50 + (level - 1) * 30


_PROFESSION_BASE: dict[Profession, dict[str, int]] = {
    Profession.WARRIOR: {"hp": 120, "mp": 30, "str": 14, "int": 6, "agi": 8, "cha": 7},
    Profession.MAGE: {"hp": 70, "mp": 80, "str": 5, "int": 16, "agi": 7, "cha": 8},
    Profession.ROGUE: {"hp": 85, "mp": 45, "str": 8, "int": 9, "agi": 15, "cha": 8},
    Profession.BARD: {"hp": 90, "mp": 55, "str": 7, "int": 10, "agi": 9, "cha": 14},
}


def _growth(prof: Profession) -> dict[str, int]:
    g = {
        Profession.WARRIOR: {"hp": 12, "mp": 3, "str": 2, "int": 0, "agi": 1, "cha": 1},
        Profession.MAGE: {"hp": 5, "mp": 10, "str": 0, "int": 2, "agi": 1, "cha": 1},
        Profession.ROGUE: {"hp": 8, "mp": 5, "str": 1, "int": 1, "agi": 2, "cha": 1},
        Profession.BARD: {"hp": 7, "mp": 7, "str": 1, "int": 1, "agi": 1, "cha": 2},
    }
    return g[prof]


@dataclass
class Player:
    """玩家运行时数据。"""

    name: str
    profession: Profession
    gender: str = "未指定"
    level: int = 1
    xp: int = 0
    gold: int = 10

    hp: int = 100
    max_hp: int = 100
    mp: int = 40
    max_mp: int = 40
    strength: int = 10
    intelligence: int = 10
    agility: int = 10
    charisma: int = 10

    inventory: Inventory = field(default_factory=lambda: Inventory(MAX_INVENTORY_SLOTS))
    equipped_weapon_id: str | None = None
    equipped_armor_id: str | None = None
    skills: list[str] = field(default_factory=list)

    @staticmethod
    def create(name: str, profession: Profession, gender: str = "未指定") -> "Player":
        """按职业创建角色并初始化属性。"""
        gn = (gender or "未指定").strip()[:32] or "未指定"
        base = _PROFESSION_BASE[profession]
        p = Player(
            name=name.strip()[:32],
            profession=profession,
            gender=gn,
            hp=base["hp"],
            max_hp=base["hp"],
            mp=base["mp"],
            max_mp=base["mp"],
            strength=base["str"],
            intelligence=base["int"],
            agility=base["agi"],
            charisma=base["cha"],
        )
        p.skills.extend(_default_skills(profession))
        return p

    def is_alive(self) -> bool:
        return self.hp > 0

    def gain_xp(self, amount: int) -> list[str]:
        """增加经验，可能升级；返回日志消息列表。"""
        msgs: list[str] = []
        self.xp += max(0, amount)
        while self.xp >= xp_for_next_level(self.level):
            self.xp -= xp_for_next_level(self.level)
            self._level_up()
            msgs.append(t("player.level_up", level=self.level))
        return msgs

    def _level_up(self) -> None:
        self.level += 1
        g = _growth(self.profession)
        self.max_hp += g["hp"]
        self.hp = min(self.hp + g["hp"], self.max_hp)
        self.max_mp += g["mp"]
        self.mp = min(self.mp + g["mp"], self.max_mp)
        self.strength += g["str"]
        self.intelligence += g["int"]
        self.agility += g["agi"]
        self.charisma += g["cha"]

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - max(0, amount))

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + max(0, amount))

    def restore_mp(self, amount: int) -> None:
        self.mp = min(self.max_mp, self.mp + max(0, amount))

    def visible_equipment_for_npc(self) -> str:
        """
        仅描述「外露装备」供 NPC 对话使用：已装备的武器/护甲名称。
        不包含背包其它物品，避免模型编造玩家持有物。
        """
        from story.items import catalog as item_catalog

        cat = item_catalog()
        parts: list[str] = []

        def _name_for(eq_id: str | None) -> str | None:
            if not eq_id:
                return None
            if eq_id in cat:
                return cat[eq_id].name
            for it in self.inventory.items:
                if it.item_id == eq_id:
                    return it.name
            return eq_id

        wn = _name_for(self.equipped_weapon_id)
        an = _name_for(self.equipped_armor_id)
        if wn:
            parts.append(t("player.visible_weapon", name=wn))
        if an:
            parts.append(t("player.visible_armor", name=an))
        if not parts:
            return t("player.visible_none")
        sep = "; " if get_narrative_language() == "en" else "；"
        return t("player.visible_summary", parts=sep.join(parts))

    def use_consumable(self, item_id: str) -> str | None:
        """使用消耗品；成功返回 None，失败返回原因。"""
        if not self.inventory.has_item(item_id, 1):
            return t("player.err.no_item")
        # 简单规则：治疗药水恢复生命
        if item_id == "healing_potion":
            self.heal(35)
            self.inventory.remove_item(item_id, 1)
            return None
        return t("player.err.cannot_use")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "profession": self.profession.value,
            "gender": self.gender,
            "level": self.level,
            "xp": self.xp,
            "gold": self.gold,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mp": self.mp,
            "max_mp": self.max_mp,
            "strength": self.strength,
            "intelligence": self.intelligence,
            "agility": self.agility,
            "charisma": self.charisma,
            "inventory": self.inventory.to_dict(),
            "equipped_weapon_id": self.equipped_weapon_id,
            "equipped_armor_id": self.equipped_armor_id,
            "skills": list(self.skills),
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Player":
        p = Player(
            name=data["name"],
            profession=Profession(data["profession"]),
            gender=str(data.get("gender", "未指定")).strip()[:32] or "未指定",
            level=int(data.get("level", 1)),
            xp=int(data.get("xp", 0)),
            gold=int(data.get("gold", 0)),
            hp=int(data["hp"]),
            max_hp=int(data["max_hp"]),
            mp=int(data["mp"]),
            max_mp=int(data["max_mp"]),
            strength=int(data["strength"]),
            intelligence=int(data["intelligence"]),
            agility=int(data["agility"]),
            charisma=int(data["charisma"]),
            inventory=Inventory.from_dict(data.get("inventory", {})),
            equipped_weapon_id=data.get("equipped_weapon_id"),
            equipped_armor_id=data.get("equipped_armor_id"),
            skills=list(data.get("skills", [])),
        )
        return p


def _default_skills(prof: Profession) -> list[str]:
    return {
        Profession.WARRIOR: ["猛击", "防御姿态"],
        Profession.MAGE: ["火球术", "法力护盾"],
        Profession.ROGUE: ["潜行", "背刺"],
        Profession.BARD: ["激励之歌", "交涉"],
    }[prof]


def item_healing_potion() -> InventoryItem:
    return InventoryItem(
        item_id="healing_potion",
        name="治疗药水",
        category=ItemCategory.CONSUMABLE,
        quantity=1,
        description="恢复少量生命值。",
    )
