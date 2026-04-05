"""队友：解析、结局判定、入队。"""

from __future__ import annotations

import copy
import random

from engine.companion_gen import parse_companion_blueprint
from engine.story_engine import StoryEngine, accept_companion_offer, decline_companion_offer
from game.companion import (
    companion_record_from_blueprint,
    fallback_companion_blueprint,
    resolve_companion_fate,
)
from game.player import Profession
from story.endings import EndingId, EndingInfo
from story.world_config import new_game_state


def test_parse_companion_blueprint() -> None:
    raw = (
        '{"name":"试炼者","appearance":"高瘦","personality":"冷","join_condition":"给钱",'
        '"special_skill":"潜行","hidden_trait_type":"间谍","hidden_trait_clue":"测试"}'
    )
    bp = parse_companion_blueprint(raw)
    assert bp is not None
    assert bp.name == "试炼者"


def test_spy_low_loyalty_always_betray() -> None:
    gs = new_game_state("p", Profession.WARRIOR.value)
    bp = fallback_companion_blueprint()
    rec = companion_record_from_blueprint(bp)
    rec["hidden_trait"]["type"] = "spy"
    rec["loyalty_score"] = 20
    info = EndingInfo(EndingId.TRAVEL, "远行", "摘要")
    fate = resolve_companion_fate(gs, rec, info, random.Random(1))
    assert fate.betrayed
    assert rec["hidden_trait"]["is_betrayer"]


def test_loyal_dog_rare_betray() -> None:
    gs = new_game_state("p", Profession.MAGE.value)
    bp = fallback_companion_blueprint()
    rec = companion_record_from_blueprint(bp)
    rec["hidden_trait"]["type"] = "loyal_dog"
    rec["loyalty_score"] = 80
    info = EndingInfo(EndingId.HERO, "英雄", "摘要")
    betray_count = 0
    for seed in range(200):
        r = copy.deepcopy(rec)
        r["loyalty_score"] = 80
        fate = resolve_companion_fate(gs, r, info, random.Random(seed))
        if fate.betrayed:
            betray_count += 1
    assert betray_count < 40


def test_accept_and_decline_offer() -> None:
    se = StoryEngine()
    gs = new_game_state("p", Profession.BARD.value)
    gs.player.gold = 50
    bp = fallback_companion_blueprint()
    gs.pending_companion_offer = companion_record_from_blueprint(bp)
    msg = accept_companion_offer(se, gs)
    assert "同行" in msg or gs.companions
    assert gs.pending_companion_offer is None
    assert any(c.get("party_status") == "active" for c in gs.companions)

    gs.pending_companion_offer = companion_record_from_blueprint(bp)
    decline_companion_offer(gs)
    assert gs.pending_companion_offer is None
