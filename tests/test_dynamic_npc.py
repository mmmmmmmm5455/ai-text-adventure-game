"""动态广场路人：解析、回退、交付数值。"""

from __future__ import annotations

from unittest.mock import patch

from engine.story_engine import StoryEngine
from game.dynamic_npc import (
    blueprint_to_record,
    clamp_gold_for_tier,
    fallback_blueprint,
    parse_blueprint,
    register_dynamic_npc_quest,
    roll_reward_tier,
)
from game.player import Profession
from story.world_config import new_game_state


def test_parse_invalid_returns_none() -> None:
    assert parse_blueprint("```not json```") is None


def test_fallback_to_record() -> None:
    bp = fallback_blueprint("rare")
    rec = blueprint_to_record(bp, "rare")
    assert rec["status"] == "fresh"
    assert rec["tier"] == "rare"
    assert rec["objective_count"] >= 1


def test_clamp_gold_respects_cap() -> None:
    assert clamp_gold_for_tier(999, "common", 100, False) <= 22
    assert clamp_gold_for_tier(999, "epic", 0, True) <= 55


def test_roll_tier_deterministic() -> None:
    import random

    rng = random.Random(42)
    tiers = [roll_reward_tier(rng) for _ in range(50)]
    assert all(t in ("common", "rare", "epic") for t in tiers)


def test_spawn_with_bad_json_uses_fallback() -> None:
    se = StoryEngine()
    gs = new_game_state("旅人", Profession.WARRIOR.value)
    gs.current_scene_id = "village_square"
    with patch(
        "engine.story_engine.generate_dynamic_npc_json",
        return_value="NOT JSON {{{",
    ):
        msg, talk = se.spawn_dynamic_npc_encounter(gs)
    assert not talk
    assert gs.dynamic_npcs
    assert gs.active_dynamic_npc_id
    assert gs.dynamic_npcs[0].get("name")
    assert len(msg) > 5


def test_deliver_after_search_progress() -> None:
    se = StoryEngine()
    gs = new_game_state("旅人", Profession.MAGE.value)
    gs.current_scene_id = "village_square"
    bp = fallback_blueprint("common")
    rec = blueprint_to_record(bp, "common")
    rec["status"] = "active"
    rec["progress"] = 1
    rec["objective_count"] = 1
    rec["reward_type"] = "gold"
    rec["reward_value"] = 10
    gs.dynamic_npcs.append(rec)
    register_dynamic_npc_quest(gs, rec)
    gold_before = gs.player.gold
    msg, talk = se.process_choice(gs, f"dyn_deliver:{rec['id']}")
    assert not talk
    assert gs.player.gold > gold_before
    assert not any(n.get("id") == rec["id"] for n in gs.dynamic_npcs)
    assert "办妥" in msg or "事情" in msg
    dq = gs.quests.get(f"dyn_{rec['id']}")
    assert dq is not None and dq.completed


def test_register_quest_shows_in_active() -> None:
    gs = new_game_state("旅人", Profession.WARRIOR.value)
    bp = fallback_blueprint("rare")
    rec = blueprint_to_record(bp, "rare")
    rec["status"] = "active"
    register_dynamic_npc_quest(gs, rec)
    names = [q.name for q in gs.quests.active_quests()]
    assert rec["name"] in names
