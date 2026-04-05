"""装备在社交对话中的印象文本。"""

from __future__ import annotations

from game.gear_social_cues import gear_public_impression, gear_trust_signal_level, npc_gear_behavior_cue
from game.player import Player, Profession


def test_gear_impression_rusty_sword() -> None:
    p = Player.create("x", Profession.WARRIOR)
    p.equipped_weapon_id = "rusty_sword"
    s = gear_public_impression(p)
    assert "生锈" in s or "新手" in s


def test_trust_signal_bounds() -> None:
    p = Player.create("x", Profession.WARRIOR)
    assert 1 <= gear_trust_signal_level(p) <= 5


def test_elder_director_mentions_patient() -> None:
    p = Player.create("x", Profession.MAGE)
    p.equipped_weapon_id = "rusty_sword"
    cue = npc_gear_behavior_cue("elder", p)
    assert "长者" in cue or "耐心" in cue


def test_merchant_director_welcoming() -> None:
    p = Player.create("x", Profession.ROGUE)
    cue = npc_gear_behavior_cue("merchant", p)
    assert "商人" in cue or "热情" in cue
