"""
角色創建系統（Character Creation System）

集成大模型推薦與手動分配，生成可導入遊戲的 Player 實例。
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

from loguru import logger

from game.inventory import InventoryItem
from game.player import Player, Profession

_CFG = Path(__file__).resolve().parents[1] / "data" / "config" / "character_creation.json"

_STAT_FULL_NAMES: dict[str, str] = {
    "str": "力量",
    "per": "感知",
    "end": "體質",
    "cha": "魅力",
    "int": "智力",
    "agl": "敏捷",
}


@dataclass
class Trait:
    id: str
    name: str
    description: str
    effects: dict[str, Any] = field(default_factory=dict)
    is_positive: bool = True


@dataclass
class Background:
    id: str
    name: str
    description: str
    recommended_traits: list[str] = field(default_factory=list)
    stat_bonus: dict[str, int] = field(default_factory=dict)
    starting_gold_bonus: int = 0
    starting_items: list[str] = field(default_factory=list)


@dataclass
class CharacterProfile:
    name: str = ""
    gender: str = ""
    background: Background | None = None
    positive_traits: list[Trait] = field(default_factory=list)
    negative_traits: list[Trait] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)

    def get_effect(self, key: str, default: Any = 0) -> Any:
        for t in self.positive_traits + self.negative_traits:
            if key in t.effects:
                return t.effects[key]
        return default

    def summary(self) -> str:
        lines = [
            f"姓名: {self.name}",
            f"性別: {self.gender}",
            f"背景: {self.background.name if self.background else '未選擇'}",
            "",
            "正面特質: " + (", ".join(t.name for t in self.positive_traits) or "無"),
            "負面特質: " + (", ".join(t.name for t in self.negative_traits) or "無"),
            "",
            "屬性:",
        ]
        keys_order = ["str", "per", "end", "cha", "int", "agl"]
        for k in keys_order:
            v = self.stats.get(k, 0)
            full = _STAT_FULL_NAMES.get(k, k)
            lines.append(f"  {full}: {v}")
        return "\n".join(lines)


def _trait_from_row(row: dict[str, Any], *, is_positive: bool) -> Trait:
    return Trait(
        id=str(row["id"]),
        name=str(row["name"]),
        description=str(row.get("description", "")),
        effects=dict(row.get("effects") or {}),
        is_positive=is_positive,
    )


def _effective_stats(
    base: dict[str, int],
    bg: Background | None,
    stat_keys: list[str],
) -> dict[str, int]:
    """創角配點（總和 20）+ 背景加成，用於寫入 Player。"""
    out = {k: int(base[k]) for k in stat_keys}
    if not bg:
        return out
    for sk, bonus in bg.stat_bonus.items():
        if sk in out:
            out[sk] = out[sk] + int(bonus)
    return out


def _merge_trait_effects(traits: list[Trait]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for t in traits:
        for k, v in t.effects.items():
            if k in merged and isinstance(merged[k], (int, float)) and isinstance(v, (int, float)):
                merged[k] = merged[k] + v
            else:
                merged[k] = v
    return merged


def _grant_starting_items(player: Player, bg: Background | None) -> None:
    if not bg or not bg.starting_items:
        return
    try:
        from story.items import catalog as items_catalog
    except ImportError:
        return
    cat = items_catalog()
    for raw_id in bg.starting_items:
        item_id = str(raw_id).strip()
        tpl = cat.get(item_id)
        if tpl is None:
            logger.warning("創角起始物品目錄無此 id，已跳過：{}", item_id)
            continue
        ok = player.inventory.add_item(InventoryItem.from_dict(tpl.to_dict()))
        if not ok:
            logger.warning("背包已滿，無法加入創角起始物品：{}", item_id)


def _background_from_row(row: dict[str, Any]) -> Background:
    items = row.get("starting_items", []) or []
    return Background(
        id=str(row["id"]),
        name=str(row["name"]),
        description=str(row.get("description", "")),
        recommended_traits=list(row.get("recommended_traits", []) or []),
        stat_bonus=dict(row.get("stat_bonus", {}) or {}),
        starting_gold_bonus=int(row.get("starting_gold_bonus", 0)),
        starting_items=[str(x) for x in items],
    )


class CharacterCreatorConfig:
    _instance: ClassVar["CharacterCreatorConfig | None"] = None

    def __init__(self, raw: dict[str, Any]) -> None:
        rules = raw.get("rules", {})
        self._stat_keys: list[str] = list(rules.get("stat_keys", ["str", "per", "end", "cha", "int", "agl"]))
        self._stat_total: int = int(rules.get("stat_points_total", 20))
        self._stat_min: int = int(rules.get("stat_min", 1))
        self._stat_max: int = int(rules.get("stat_max", 10))
        self._auto_min: int = int(rules.get("auto_stat_min", 1))
        self._auto_max: int = int(rules.get("auto_stat_max", 8))
        self._max_pos: int = int(rules.get("max_positive_traits", 2))
        self._max_neg: int = int(rules.get("max_negative_traits", 2))

        self._backgrounds: dict[str, Background] = {}
        for row in raw.get("backgrounds", []):
            b = _background_from_row(row)
            self._backgrounds[b.id] = b

        self._positive_traits: dict[str, Trait] = {}
        self._negative_traits: dict[str, Trait] = {}
        tdata = raw.get("traits", {})
        for row in tdata.get("positive", []):
            t = _trait_from_row(row, is_positive=True)
            self._positive_traits[t.id] = t
        for row in tdata.get("negative", []):
            t = _trait_from_row(row, is_positive=False)
            self._negative_traits[t.id] = t

    @classmethod
    def get_instance(cls) -> CharacterCreatorConfig:
        if cls._instance is None:
            raw = json.loads(_CFG.read_text(encoding="utf-8"))
            cls._instance = cls(raw)
        return cls._instance

    @classmethod
    def _reset_instance_for_tests(cls) -> None:
        cls._instance = None

    @classmethod
    def reload(cls) -> CharacterCreatorConfig:
        """重新讀取 JSON（開發時改設定檔後呼叫）。"""
        cls._instance = None
        return cls.get_instance()

    @property
    def backgrounds(self) -> list[Background]:
        return list(self._backgrounds.values())

    @property
    def positive_traits(self) -> list[Trait]:
        return list(self._positive_traits.values())

    @property
    def negative_traits(self) -> list[Trait]:
        return list(self._negative_traits.values())

    def get_background(self, bg_id: str) -> Background | None:
        return self._backgrounds.get(bg_id)

    def get_trait(self, trait_id: str) -> Trait | None:
        return self._positive_traits.get(trait_id) or self._negative_traits.get(trait_id)

    def list_background_ids(self) -> list[str]:
        return list(self._backgrounds.keys())

    def get_random_background(self) -> Background:
        return random.choice(list(self._backgrounds.values()))

    def get_random_traits(self) -> tuple[list[Trait], list[Trait]]:
        pvals = list(self._positive_traits.values())
        nvals = list(self._negative_traits.values())
        kp = min(2, len(pvals))
        kn = min(2, len(nvals))
        pos = random.sample(pvals, k=kp) if kp else []
        neg = random.sample(nvals, k=kn) if kn else []
        return pos, neg


class CharacterCreator:
    """手動／隨機創角流程，可選接入大模型背景。"""

    def __init__(self, config: CharacterCreatorConfig | None = None) -> None:
        self.config = config or CharacterCreatorConfig.get_instance()
        self.profile = CharacterProfile()

    @staticmethod
    def quick_random(
        llm_client: Any | None = None,
        *,
        config: CharacterCreatorConfig | None = None,
    ) -> Player:
        cfg = config or CharacterCreatorConfig.get_instance()
        creator = CharacterCreator(cfg)
        creator.set_name(random.choice(["阿卡", "艾拉", "羅根", "莉莉"]))
        creator.set_gender(random.choice(["男", "女", "不詳"]))
        creator.choose_background(random.choice(cfg.list_background_ids()))
        creator.auto_distribute_random()
        if creator.profile.background:
            creator.add_recommended_traits(creator.profile.background)
        if llm_client:
            try:
                result = llm_client.generate_character_background_sync(creator.profile.name)
                if result:
                    creator.accept_llm_result(result)
            except Exception as e:
                logger.warning("LLM 快速創角背景生成失敗，沿用隨機結果：{}", e)
        return creator.build()

    def set_name(self, name: str) -> CharacterCreator:
        self.profile.name = (name or "").strip()[:64]
        return self

    def set_gender(self, gender: str) -> CharacterCreator:
        self.profile.gender = (gender or "").strip()[:32]
        return self

    def choose_background(self, bg_id: str) -> CharacterCreator:
        bg = self.config.get_background(bg_id)
        if not bg:
            raise ValueError(f"無效的背景ID: {bg_id}")
        self.profile.background = bg
        return self

    def add_trait(self, tid: str, *, positive: bool = True) -> CharacterCreator:
        pool = self.config._positive_traits if positive else self.config._negative_traits
        current = self.profile.positive_traits if positive else self.profile.negative_traits
        opposite = self.profile.negative_traits if positive else self.profile.positive_traits
        limit = self.config._max_pos if positive else self.config._max_neg

        if tid not in pool:
            raise ValueError(f"無效的特質ID: {tid}")
        if any(t.id == tid for t in current):
            raise ValueError(f"特質已存在: {pool[tid].name}")
        if len(current) >= limit:
            raise ValueError(f"{'正面' if positive else '負面'}特質已達上限")
        if any(t.id == tid for t in opposite):
            raise ValueError(f"無法同時擁有正反兩種「{pool[tid].name}」")

        current.append(pool[tid])
        return self

    def add_recommended_traits(self, bg: Background) -> CharacterCreator:
        for tid in bg.recommended_traits:
            try:
                self.add_trait(tid, positive=True)
            except ValueError:
                pass
        return self

    def distribute_stats(self, stats: dict[str, int]) -> CharacterCreator:
        keys = self.config._stat_keys
        if set(stats.keys()) != set(keys):
            raise ValueError("屬性鍵與規則不符")
        for k, v in stats.items():
            if not (self.config._stat_min <= v <= self.config._stat_max):
                raise ValueError(f"{k} 必須在 1~10 之間")
        total = sum(stats.values())
        if total != self.config._stat_total:
            raise ValueError(f"屬性總和必須為{self.config._stat_total}，目前: {total}")
        self.profile.stats = dict(stats)
        return self

    def auto_distribute_random(self) -> CharacterCreator:
        keys = self.config._stat_keys
        n = len(keys)
        lo, hi = self.config._auto_min, self.config._auto_max
        total = self.config._stat_total
        base = [lo] * n
        remaining = total - lo * n
        while remaining > 0:
            idx = random.randrange(n)
            if base[idx] < hi:
                base[idx] += 1
                remaining -= 1
        self.profile.stats = {k: base[i] for i, k in enumerate(keys)}
        return self

    def accept_llm_result(self, llm_result: dict[str, Any]) -> CharacterCreator:
        items_raw = llm_result.get("starting_items", []) or []
        bg = Background(
            id=str(llm_result.get("background_id", "llm_generated")),
            name=str(llm_result.get("name", "未知背景")),
            description=str(llm_result.get("description", "")),
            recommended_traits=list(llm_result.get("recommended_traits", []) or []),
            stat_bonus=dict(llm_result.get("stat_bonus", {}) or {}),
            starting_gold_bonus=int(llm_result.get("starting_gold_bonus", 0)),
            starting_items=[str(x) for x in items_raw],
        )
        self.profile.background = bg
        self.profile.positive_traits.clear()
        self.profile.negative_traits.clear()
        # 配點與手動流程一致：總和 20；背景 stat_bonus 僅在 build() 時加成
        self.auto_distribute_random()
        for tid in bg.recommended_traits:
            t = self.config.get_trait(tid)
            if t and t.is_positive:
                try:
                    self.add_trait(tid, positive=True)
                except ValueError:
                    pass
        return self

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not (self.profile.name or "").strip():
            errors.append("請輸入姓名")
        if not self.profile.background:
            errors.append("請選擇背景")
        if not self.profile.stats:
            errors.append(f"屬性總和必須為{self.config._stat_total}，目前: 0")
        elif set(self.profile.stats.keys()) != set(self.config._stat_keys):
            errors.append("屬性項目不完整")
        elif any(
            not (self.config._stat_min <= v <= self.config._stat_max)
            for v in self.profile.stats.values()
        ):
            errors.append("屬性單項必須在規則範圍內")
        else:
            s = sum(self.profile.stats.values())
            if s != self.config._stat_total:
                errors.append(f"屬性總和必須為{self.config._stat_total}，目前: {s}")
        return errors

    def build(self, *, profession: Profession | None = None) -> Player:
        if errors := self.validate():
            raise ValueError(f"創建角色失敗: {', '.join(errors)}")

        prof = profession if profession is not None else Profession.WARRIOR
        bg = self.profile.background
        name = (self.profile.name or "").strip()[:32]
        gender = (self.profile.gender or "未指定").strip()[:32] or "未指定"
        player = Player.create(name=name, profession=prof, gender=gender)

        player.traits = [t.id for t in self.profile.positive_traits + self.profile.negative_traits]
        player.background_id = bg.id if bg else None
        player.background_name = bg.name if bg else None
        player.trait_effects = _merge_trait_effects(
            self.profile.positive_traits + self.profile.negative_traits
        )

        stat_map = {
            "str": "strength",
            "per": "perception",
            "end": "endurance",
            "cha": "charisma",
            "int": "intelligence",
            "agl": "agility",
        }
        eff = _effective_stats(self.profile.stats, bg, self.config._stat_keys)
        for k, v in eff.items():
            attr = stat_map.get(k)
            if attr:
                setattr(player, attr, int(v))

        gold_bonus = bg.starting_gold_bonus if bg else 0
        player.gold = 20 + gold_bonus
        _grant_starting_items(player, bg)
        return player


def load_character_creation_config() -> CharacterCreatorConfig:
    return CharacterCreatorConfig.get_instance()
