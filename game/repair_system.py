"""
装备耐久与修理规则：读取 JSON 配置并执行自修/NPC 修理。

- `RepairResult`：結論枚舉（SUCCESS / FAIL / CRITICAL_SUCCESS，CRITICAL 為別名）
- `RepairReceipt`：單次修理完整回傳（`success`、`result`、`materials_used` 等）
- `RepairOutcome`：精簡資料結構（測試／事件用）
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any, ClassVar

from core.i18n import t
from game.inventory import Inventory, InventoryItem, ItemCategory

_CFG_PATH = Path(__file__).resolve().parents[1] / "data" / "config" / "repair_system.json"
_NPC_SCENE_ALIAS = {
    "village_square": "village_repair_stand",
    "tavern": "town_blacksmith",
}
_SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "smithing": ("smithing", "锻造", "打铁"),
    "tailoring": ("tailoring", "缝纫", "裁缝"),
}


class RepairError(Exception):
    """修理流程錯誤基類。"""


class ItemNotRepairable(RepairError):
    """物品分類不可修理或不存在。"""


class InsufficientMaterials(RepairError):
    """材料不足。"""


class InsufficientGold(RepairError):
    """金幣不足。"""


class ItemNotBroken(RepairError):
    """耐久已滿或不需要修理。"""


class ConditionNotMet(RepairError):
    """技能、地點、菌人／次元條件不滿足。"""


class RepairMethod(str, Enum):
    SELF = "self"
    NPC = "npc"
    EMERGENCY = "emergency"
    ENCHANTED = "enchanted"
    MOLD = "mold"
    DIMENSIONAL = "dimensional"


class RepairResult(str, Enum):
    """單次修理結論（與 `RepairReceipt.result` 對應）。"""

    SUCCESS = "success"
    FAIL = "fail"
    CRITICAL_SUCCESS = "critical"
    CRITICAL = "critical"  # 與 CRITICAL_SUCCESS 同值，語意別名


@lru_cache(maxsize=1)
def load_repair_config() -> dict[str, Any]:
    return json.loads(_CFG_PATH.read_text(encoding="utf-8"))


@dataclass
class RepairConfig:
    """`repair_system.json` 的包裝。"""

    raw: dict[str, Any]
    _singleton: ClassVar["RepairConfig | None"] = None

    @classmethod
    def load_default(cls) -> RepairConfig:
        return cls(load_repair_config())

    @classmethod
    def get_instance(cls) -> RepairConfig:
        if cls._singleton is None:
            cls._singleton = cls(load_repair_config())
        return cls._singleton

    @property
    def repair_formula(self) -> dict[str, Any]:
        return self.raw["repair_formula"]

    @property
    def repair_randomness(self) -> dict[str, Any]:
        return self.raw["repair_randomness"]

    @property
    def special_repairs(self) -> dict[str, Any]:
        return self.raw["special_repairs"]

    def get_item_category_config(self, key: str) -> dict[str, Any]:
        return dict(self.raw.get("item_categories", {}).get(key, {}))


@dataclass
class RepairReceipt:
    """`attempt_repair` / `attempt_equipped` 的回傳物件。"""

    result: RepairResult
    message: str
    durability_restored: int = 0
    gold_spent: int = 0
    was_critical: bool = False
    backfire_max_durability_lost: int = 0
    method: RepairMethod | None = None
    error_code: str | None = None
    materials_used: list[str] = field(default_factory=list)
    hp_cost: int = 0

    @property
    def ok(self) -> bool:
        return self.result in (RepairResult.SUCCESS, RepairResult.CRITICAL_SUCCESS)

    @property
    def success(self) -> bool:
        return self.ok

    @property
    def outcome(self) -> RepairResult:
        return self.result


@dataclass
class RepairOutcome:
    """精簡修理結果（事件／教學測試用）。"""

    result: RepairResult
    item_id: str
    method: RepairMethod
    durability_restored: int = 0

    @property
    def success(self) -> bool:
        return self.result in (RepairResult.SUCCESS, RepairResult.CRITICAL_SUCCESS)

    @property
    def was_critical(self) -> bool:
        return self.result is RepairResult.CRITICAL_SUCCESS


@dataclass
class RepairContext:
    state: Any
    slot: str
    via_npc: bool = False
    mode: str = "standard"


def _repair_method_from_context(ctx: RepairContext) -> RepairMethod:
    if ctx.via_npc:
        return RepairMethod.NPC
    if ctx.mode == "emergency":
        return RepairMethod.EMERGENCY
    if ctx.mode == "enchanted":
        return RepairMethod.ENCHANTED
    return RepairMethod.SELF


class _DictPlayerProxy:
    """讓 dict 玩家在修理流程內可 setattr，並回寫 gold/hp 等欄位。"""

    def __init__(self, data: dict[str, Any], inv: Inventory, profession_obj: Any) -> None:
        object.__setattr__(self, "_d", data)
        object.__setattr__(self, "inventory", inv)
        object.__setattr__(self, "profession", profession_obj)

    def __getattr__(self, name: str) -> Any:
        extra = object.__getattribute__(self, "__dict__")
        if name in extra and name not in ("_d", "inventory", "profession"):
            return extra[name]
        d = object.__getattribute__(self, "_d")
        if name in d:
            return d[name]
        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_d", "inventory", "profession"):
            object.__setattr__(self, name, value)
            return
        d = object.__getattribute__(self, "_d")
        if name in d:
            d[name] = value
        else:
            object.__getattribute__(self, "__dict__")[name] = value


class RepairSystem:
    __slots__ = ("_player", "_inventory", "_cfg")

    def __init__(
        self,
        player: Any = None,
        inventory: Inventory | None = None,
        *,
        cfg: dict[str, Any] | None = None,
    ) -> None:
        self._player = player
        self._inventory = inventory
        self._cfg = cfg if cfg is not None else load_repair_config()

    @property
    def cfg(self) -> dict[str, Any]:
        return self._cfg

    def _find_item(self, item_id: str) -> InventoryItem | None:
        if self._inventory is None:
            return None
        return self._inventory.find_item(item_id)

    def get_available_methods(self, item_id: str, *, scene_id: str = "village_square") -> list[RepairMethod]:
        if self._inventory is None:
            return []
        it = self._inventory.find_item(item_id)
        if it is None or not is_repairable(it, self._cfg):
            return []
        raw = self._player
        cfg = self._cfg
        man = (
            bool(raw.get("is_mancelled", False))
            if isinstance(raw, dict)
            else bool(getattr(raw, "is_mancelled", False))
        )
        order = [
            RepairMethod.SELF,
            RepairMethod.NPC,
            RepairMethod.EMERGENCY,
            RepairMethod.ENCHANTED,
            RepairMethod.DIMENSIONAL,
        ]
        if man and cfg.get("special_repairs", {}).get("mold_repair", {}).get("enabled", True):
            order.append(RepairMethod.MOLD)
        if not can_npc_repair_here(scene_id, cfg):
            order = [m for m in order if m != RepairMethod.NPC]
        return order

    def get_repair_cost_estimate(self, item_id: str, method: RepairMethod) -> dict[RepairMethod, dict[str, Any]]:
        out: dict[RepairMethod, dict[str, Any]] = {}
        if method == RepairMethod.NPC:
            out[RepairMethod.NPC] = {"success_rate": "100%"}
        return out

    def attempt_repair(
        self,
        item_id: str,
        method: RepairMethod = RepairMethod.SELF,
        *,
        scene_id: str = "village_square",
    ) -> RepairReceipt:
        return self.repair_item(item_id, method, scene_id=scene_id)

    def repair_item(
        self,
        item_id: str,
        method: RepairMethod = RepairMethod.SELF,
        *,
        scene_id: str = "village_square",
    ) -> RepairReceipt:
        if self._inventory is None or self._player is None:
            raise RepairError("使用 repair_item() 時建構子必須傳入 player 與 inventory")
        inv = self._inventory
        it = inv.find_item(item_id)
        if it is None:
            raise ItemNotRepairable(t("repair.err.missing_item", name=item_id))
        cfg = self._cfg
        if not is_repairable(it, cfg):
            raise ItemNotRepairable(t("repair.err.not_repairable", name=it.name))
        cur, max_d = ensure_durability(it, cfg)
        if cur >= max_d:
            raise ItemNotBroken(t("repair.err.full", name=it.name))

        if method == RepairMethod.MOLD:
            return self._repair_mold(it, scene_id)
        if method == RepairMethod.DIMENSIONAL:
            return self._repair_dimensional(it)

        state = self._make_mini_state(self._player, inv, scene_id, item_id, it.category)
        via_npc = method == RepairMethod.NPC
        mode = {
            RepairMethod.SELF: "standard",
            RepairMethod.NPC: "standard",
            RepairMethod.EMERGENCY: "emergency",
            RepairMethod.ENCHANTED: "enchanted",
        }[method]
        slot = "weapon" if it.category == ItemCategory.WEAPON else "armor"
        res = self.attempt_equipped(RepairContext(state=state, slot=slot, via_npc=via_npc, mode=mode))
        if res.ok:
            return res
        code = res.error_code or ""
        if code in ("repair.fail.normal", "repair.fail.backfire"):
            return res
        if code == "repair.err.material_missing":
            raise InsufficientMaterials(res.message)
        if code == "repair.err.not_enough_gold":
            raise InsufficientGold(res.message)
        if code == "repair.err.full":
            raise ItemNotBroken(res.message)
        if code == "repair.err.not_repairable":
            raise ItemNotRepairable(res.message)
        if code in {
            "repair.err.untrained",
            "repair.err.no_npc_here",
            "repair.err.no_item_equipped",
            "repair.err.no_player",
        }:
            raise ConditionNotMet(res.message)
        return res

    def _repair_mold(self, it: InventoryItem, scene_id: str) -> RepairReceipt:
        raw = self._player
        cfg = self._cfg
        man = (
            bool(raw.get("is_mancelled", False))
            if isinstance(raw, dict)
            else bool(getattr(raw, "is_mancelled", False))
        )
        if not man:
            raise ConditionNotMet(t("repair.err.mold_only", name=it.name))
        spec = cfg.get("special_repairs", {}).get("mold_repair", {})
        hp_cost = int(spec.get("hp_cost", 10))
        hp = _player_hp(raw)
        if hp < hp_cost:
            raise ConditionNotMet(t("repair.err.mold_hp", need=hp_cost))
        pct = float(spec.get("durability_restored_percent", 0.5))
        cur, max_d = ensure_durability(it, cfg)
        restore = max(1, int(max_d * pct))
        _apply_hp_change(raw, hp - hp_cost)
        it.meta["durability"] = min(max_d, cur + restore)
        return RepairReceipt(
            result=RepairResult.SUCCESS,
            message=t("repair.ok.mold", name=it.name, restored=restore),
            durability_restored=restore,
            method=RepairMethod.MOLD,
            hp_cost=hp_cost,
        )

    def _repair_dimensional(self, it: InventoryItem) -> RepairReceipt:
        raw = self._player
        cfg = self._cfg
        fr = _player_fragments(raw)
        if fr < 1:
            raise ConditionNotMet(t("repair.err.no_fragment", name=it.name))
        cur, max_d = ensure_durability(it, cfg)
        _apply_fragments(raw, fr - 1)
        restored = max_d - cur
        it.meta["durability"] = max_d
        return RepairReceipt(
            result=RepairResult.SUCCESS,
            message=t("repair.ok.dimensional", name=it.name),
            durability_restored=restored,
            method=RepairMethod.DIMENSIONAL,
        )

    def _tags_from_raw(self, raw: Any) -> set[str]:
        if isinstance(raw, dict):
            tgs = raw.get("tags", [])
            return set(tgs) if isinstance(tgs, (list, set, tuple)) else set()
        raw_tags = getattr(raw, "tags", set())
        return set(raw_tags) if raw_tags is not None else set()

    def _wrap_player(self, raw: Any, inv: Inventory) -> Any:
        if isinstance(raw, dict):
            prof = raw.get("profession")
            if isinstance(prof, str):
                prof_obj: Any = SimpleNamespace(name=prof.upper())
            elif prof is not None and hasattr(prof, "name"):
                prof_obj = prof
            else:
                prof_obj = SimpleNamespace(name="MAGE")
            if "skills" not in raw:
                raw["skills"] = []
            return _DictPlayerProxy(raw, inv, prof_obj)
        return raw

    def _make_mini_state(self, raw_player: Any, inv: Inventory, scene_id: str, item_id: str, category: ItemCategory) -> Any:
        p = self._wrap_player(raw_player, inv)
        if category == ItemCategory.WEAPON:
            p.equipped_weapon_id = item_id
            if not hasattr(p, "equipped_armor_id"):
                p.equipped_armor_id = None
        elif category == ItemCategory.ARMOR:
            p.equipped_armor_id = item_id
            if not hasattr(p, "equipped_weapon_id"):
                p.equipped_weapon_id = None
        else:
            raise ItemNotRepairable(t("repair.err.not_repairable", name=item_id))
        tags = self._tags_from_raw(raw_player)
        return SimpleNamespace(player=p, current_scene_id=scene_id, tags=tags, touch=lambda: None)

    def attempt_equipped(self, ctx: RepairContext) -> RepairReceipt:
        cfg = self._cfg
        state = ctx.state
        slot = ctx.slot
        via_npc = ctx.via_npc
        mode = ctx.mode
        rm = _repair_method_from_context(ctx)
        player = getattr(state, "player", None)
        if not player:
            return RepairReceipt(
                RepairResult.FAIL,
                t("repair.err.no_player"),
                error_code="repair.err.no_player",
                method=rm,
            )

        item = get_equipped_item(state, slot)
        if not item:
            return RepairReceipt(
                RepairResult.FAIL,
                t("repair.err.no_item_equipped", slot=t(f"repair.slot.{slot}")),
                error_code="repair.err.no_item_equipped",
                method=rm,
            )
        if not is_repairable(item, cfg):
            return RepairReceipt(
                RepairResult.FAIL,
                t("repair.err.not_repairable", name=item.name),
                error_code="repair.err.not_repairable",
                method=rm,
            )

        cur, max_d = ensure_durability(item, cfg)
        if cur >= max_d:
            return RepairReceipt(
                RepairResult.FAIL,
                t("repair.err.full", name=item.name),
                error_code="repair.err.full",
                method=rm,
            )

        if via_npc:
            if not can_npc_repair_here(getattr(state, "current_scene_id", ""), cfg):
                return RepairReceipt(
                    RepairResult.FAIL,
                    t("repair.err.no_npc_here"),
                    error_code="repair.err.no_npc_here",
                    method=rm,
                )
            lost_ratio = (max_d - cur) / max(1, max_d)
            mult = float(cfg.get("npc_repair", {}).get("cost_multiplier", 0.5))
            base_v = int(item.meta.get("base_value", 0))
            cost = int(base_v * lost_ratio * mult)
            min_cost = int(cfg.get("npc_repair_pricing", {}).get("min_cost", 5))
            cost = max(min_cost, cost)
            if player.gold < cost:
                return RepairReceipt(
                    RepairResult.FAIL,
                    t("repair.err.not_enough_gold", gold=cost),
                    error_code="repair.err.not_enough_gold",
                    method=rm,
                )
            player.gold -= cost
            item.meta["durability"] = max_d
            state.touch()
            restored = max_d - cur
            return RepairReceipt(
                RepairResult.SUCCESS,
                t("repair.ok.npc", name=item.name, gold=cost),
                durability_restored=restored,
                gold_spent=cost,
                method=rm,
            )

        cat = _cat_cfg(item, cfg)
        required_skill = str(cat.get("repair_skill_required", "smithing"))
        skill_cfg = cfg.get("skill_checks", {}).get(required_skill, {})
        if bool(skill_cfg.get("trained_only", False)) and not _trained_for(player, required_skill):
            return RepairReceipt(
                RepairResult.FAIL,
                t("repair.err.untrained", skill=required_skill),
                error_code="repair.err.untrained",
                method=rm,
            )

        mat_id, mat_amt = _repair_material_for(item, cfg)
        if mode == "emergency":
            mul = float(
                cfg.get("special_repairs", {})
                .get("emergency_repair", {})
                .get("material_cost_multiplier", 2.0)
            )
            mat_amt = max(1, int(round(mat_amt * mul)))
        if not player.inventory.has_item(mat_id, mat_amt):
            return RepairReceipt(
                RepairResult.FAIL,
                t("repair.err.material_missing", material=mat_id, amount=mat_amt),
                error_code="repair.err.material_missing",
                method=rm,
            )

        formula = cfg.get("repair_formula", {})
        rand_cfg = cfg.get("repair_randomness", {})
        stat_name = str(
            skill_cfg.get("stat", cfg.get("general_rules", {}).get("repair_skill_attribute", "intelligence"))
        )
        rate = float(formula.get("base_success_rate", 0.6))
        rate += _player_stat(player, stat_name) * float(formula.get("skill_bonus_per_point", 0.05))
        for tag, bonus in dict(formula.get("trait_bonuses", {})).items():
            if tag in getattr(state, "tags", set()):
                rate += float(bonus)
        if mode == "enchanted":
            spec = cfg.get("special_repairs", {}).get("enchanted_repair", {})
            req = str(spec.get("material_required", "enchanted_dust"))
            req_n = int(spec.get("material_amount", 1))
            if not player.inventory.has_item(req, req_n):
                return RepairReceipt(
                    RepairResult.FAIL,
                    t("repair.err.material_missing", material=req, amount=req_n),
                    error_code="repair.err.material_missing",
                    method=rm,
                )
            rate += float(spec.get("skill_bonus_extra", 0.2))

        rate = max(float(formula.get("min_success_rate", 0.1)), min(float(formula.get("max_success_rate", 0.95)), rate))
        save_material = random.random() < float(rand_cfg.get("material_saving_chance", 0.1))
        mats_used: list[str] = []
        if not save_material:
            player.inventory.remove_item(mat_id, mat_amt)
            mats_used.append(mat_id)

        if mode == "emergency":
            pct = float(
                cfg.get("special_repairs", {})
                .get("emergency_repair", {})
                .get("durability_restored_percent", 0.3)
            )
            restore = max(1, int(max_d * pct))
            item.meta["durability"] = min(max_d, cur + restore)
            state.touch()
            return RepairReceipt(
                RepairResult.SUCCESS,
                t("repair.ok.emergency", name=item.name, restored=restore),
                durability_restored=restore,
                method=rm,
                materials_used=mats_used,
            )

        success = random.random() < rate
        if success:
            if mode == "enchanted":
                spec_e = cfg.get("special_repairs", {}).get("enchanted_repair", {})
                req_e = str(spec_e.get("material_required", "enchanted_dust"))
                req_ne = int(spec_e.get("material_amount", 1))
                player.inventory.remove_item(req_e, req_ne)
                mats_used.append(req_e)
            crit_rate = float(rand_cfg.get("critical_success_chance", 0.05))
            if mode == "enchanted":
                crit_rate += float(
                    cfg.get("special_repairs", {})
                    .get("enchanted_repair", {})
                    .get("crit_chance_bonus", 0.15)
                )
            if random.random() < crit_rate and bool(rand_cfg.get("critical_success_repair_full", True)):
                restored = max_d - cur
                item.meta["durability"] = max_d
                state.touch()
                return RepairReceipt(
                    RepairResult.CRITICAL,
                    t("repair.ok.critical", name=item.name),
                    durability_restored=restored,
                    was_critical=True,
                    method=rm,
                    materials_used=mats_used,
                )
            low = int(rand_cfg.get("durability_restored_min", 10))
            high = int(rand_cfg.get("durability_restored_max", 40))
            restore = max(1, random.randint(min(low, high), max(low, high)))
            item.meta["durability"] = min(max_d, cur + restore)
            state.touch()
            return RepairReceipt(
                RepairResult.SUCCESS,
                t("repair.ok.success", name=item.name, restored=restore),
                durability_restored=restore,
                method=rm,
                materials_used=mats_used,
            )

        if random.random() < float(rand_cfg.get("backfire_chance", 0.03)):
            loss = max(1, random.randint(1, int(rand_cfg.get("backfire_max_durability_loss", 5))))
            item.meta["max_durability"] = max(1, max_d - loss)
            item.meta["durability"] = min(int(item.meta["durability"]), int(item.meta["max_durability"]))
            state.touch()
            return RepairReceipt(
                RepairResult.FAIL,
                t("repair.fail.backfire", name=item.name, loss=loss),
                backfire_max_durability_lost=loss,
                error_code="repair.fail.backfire",
                method=rm,
                materials_used=mats_used,
            )
        state.touch()
        return RepairReceipt(
            RepairResult.FAIL,
            t("repair.fail.normal", name=item.name),
            error_code="repair.fail.normal",
            method=rm,
            materials_used=mats_used,
        )


def _player_hp(raw: Any) -> int:
    if isinstance(raw, dict):
        return int(raw.get("hp", 0))
    return int(getattr(raw, "hp", 0))


def _apply_hp_change(raw: Any, new_hp: int) -> None:
    if isinstance(raw, dict):
        raw["hp"] = new_hp
    else:
        setattr(raw, "hp", new_hp)


def _player_fragments(raw: Any) -> int:
    if isinstance(raw, dict):
        return int(raw.get("dimensional_fragments", 0))
    return int(getattr(raw, "dimensional_fragments", 0))


def _apply_fragments(raw: Any, new_n: int) -> None:
    if isinstance(raw, dict):
        raw["dimensional_fragments"] = new_n
    else:
        setattr(raw, "dimensional_fragments", new_n)


def _cat_key(item: InventoryItem) -> str:
    return item.category.name


def _cat_cfg(item: InventoryItem, cfg: dict[str, Any]) -> dict[str, Any]:
    return cfg.get("item_categories", {}).get(_cat_key(item), {})


def _find_item(state: Any, item_id: str) -> InventoryItem | None:
    p = getattr(state, "player", None)
    if not p:
        return None
    for it in p.inventory.items:
        if it.item_id == item_id:
            return it
    return None


def get_equipped_item(state: Any, slot: str) -> InventoryItem | None:
    p = getattr(state, "player", None)
    if not p:
        return None
    item_id = p.equipped_weapon_id if slot == "weapon" else p.equipped_armor_id
    if not item_id:
        return None
    return _find_item(state, item_id)


def ensure_durability(item: InventoryItem, cfg: dict[str, Any] | None = None) -> tuple[int, int]:
    cfg = cfg or load_repair_config()
    c = _cat_cfg(item, cfg)
    if not c.get("repairable", False):
        return 0, 0
    max_d = int(item.meta.get("max_durability", c.get("default_max_durability", 50)))
    cur_d = int(item.meta.get("durability", max_d))
    cur_d = max(0, min(max_d, cur_d))
    item.meta["max_durability"] = max_d
    item.meta["durability"] = cur_d
    if "base_value" not in item.meta:
        base_per = int(cfg.get("npc_repair", {}).get("base_value_per_durability", 2))
        item.meta["base_value"] = max_d * base_per
    return cur_d, max_d


def is_repairable(item: InventoryItem, cfg: dict[str, Any] | None = None) -> bool:
    cfg = cfg or load_repair_config()
    return bool(_cat_cfg(item, cfg).get("repairable", False))


def is_broken(item: InventoryItem, cfg: dict[str, Any] | None = None) -> bool:
    if not is_repairable(item, cfg):
        return False
    cur, _ = ensure_durability(item, cfg)
    return cur <= 0


def durability_ratio(item: InventoryItem, cfg: dict[str, Any] | None = None) -> float:
    cur, max_d = ensure_durability(item, cfg)
    if max_d <= 0:
        return 1.0
    return cur / max_d


def durability_text(item: InventoryItem, cfg: dict[str, Any] | None = None) -> str:
    if not is_repairable(item, cfg):
        return ""
    cur, max_d = ensure_durability(item, cfg)
    return t("repair.durability", cur=cur, max=max_d)


def can_npc_repair_here(scene_id: str, cfg: dict[str, Any] | None = None) -> bool:
    cfg = cfg or load_repair_config()
    allowed = set(cfg.get("npc_repair", {}).get("available_locations", []))
    if scene_id in allowed:
        return True
    alias = _NPC_SCENE_ALIAS.get(scene_id)
    return alias in allowed


def has_damaged_equipped(state: Any, slot: str) -> bool:
    it = get_equipped_item(state, slot)
    if not it or not is_repairable(it):
        return False
    cur, max_d = ensure_durability(it)
    return cur < max_d


def _repair_material_for(item: InventoryItem, cfg: dict[str, Any]) -> tuple[str, int]:
    c = _cat_cfg(item, cfg)
    typ = str(c.get("repair_material_type", "metal"))
    if typ == "metal":
        return "metal_scraps", 1
    return "leather_pieces", 1


def _trained_for(player: Any, required_skill: str) -> bool:
    aliases = _SKILL_ALIASES.get(required_skill, (required_skill,))
    if isinstance(player, dict):
        pool = {str(s).lower() for s in player.get("skills", [])}
        prof = player.get("profession")
        if isinstance(prof, str):
            prof_name = prof.upper()
        elif prof is not None and hasattr(prof, "name"):
            prof_name = str(getattr(prof, "name", ""))
        else:
            prof_name = ""
    else:
        pool = {str(s).lower() for s in getattr(player, "skills", [])}
        prof = getattr(player, "profession", None)
        prof_name = str(getattr(prof, "name", prof) or "")
    for a in aliases:
        if a.lower() in pool:
            return True
    if required_skill == "smithing":
        return prof_name in {"WARRIOR"}
    if required_skill == "tailoring":
        return prof_name in {"ROGUE", "BARD"}
    return False


def _player_stat(player: Any, name: str) -> int:
    if isinstance(player, dict):
        v = player.get(name, 0)
        return int(v) if v is not None else 0
    return int(getattr(player, name, 0))


def attempt_equipped_repair(state: Any, slot: str, via_npc: bool = False, mode: str = "standard") -> str:
    ctx = RepairContext(state=state, slot=slot, via_npc=via_npc, mode=mode)
    return RepairSystem().attempt_equipped(ctx).message

