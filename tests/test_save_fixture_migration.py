"""模拟旧版存档形态，经迁移后应可加载。"""

from __future__ import annotations

import copy

from game.game_state import GameState
from game.player import Profession
from story.world_config import new_game_state


def _strip_to_schema_v3(d: dict) -> dict:
    out = copy.deepcopy(d)
    out["schema_version"] = 3
    for k in (
        "flavor_log",
        "world_flags",
        "world_evolution",
        "stat_counters",
        "pending_gift_box",
        "meta_break_budget",
        "narrative_achievement_ids",
        "newspaper_issue",
    ):
        out.pop(k, None)
    return out


def test_load_after_stripping_v4_fields_migrates() -> None:
    gs = new_game_state("迁移", Profession.ROGUE.value, gender="女")
    raw = gs.to_dict()
    v3ish = _strip_to_schema_v3(raw)
    gs2 = GameState.from_dict(v3ish)
    assert gs2.flavor_log == []
    assert gs2.meta_break_budget == 3
    assert gs2.player and gs2.player.name == "迁移"


def test_schema_v2_shape_gets_companion_defaults() -> None:
    """缺 companions 等 v3 字段的旧 dict 应被迁移补齐。"""
    gs = new_game_state("旧档", Profession.MAGE.value)
    raw = gs.to_dict()
    raw["schema_version"] = 2
    for k in (
        "companions",
        "pending_companion_offer",
        "companion_fate_log",
        "flavor_log",
        "world_flags",
        "world_evolution",
        "stat_counters",
        "pending_gift_box",
        "meta_break_budget",
        "narrative_achievement_ids",
        "newspaper_issue",
    ):
        raw.pop(k, None)
    gs2 = GameState.from_dict(raw)
    assert isinstance(gs2.companions, list)
    assert gs2.pending_companion_offer is None
    assert gs2.flavor_log == []
