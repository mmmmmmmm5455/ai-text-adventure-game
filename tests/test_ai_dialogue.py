"""对话引擎测试。"""

from __future__ import annotations

from unittest.mock import patch

from engine.ai_dialogue import AIDialogueEngine, DialogueSession
from game.player import Profession
from story import characters as ch
from story.world_config import new_game_state


def test_dialogue_opening_contains_npc_or_fallback() -> None:
    eng = AIDialogueEngine()
    gs = new_game_state("对话者", Profession.ROGUE.value)
    text = eng.start_dialogue(gs, "elder")
    assert len(text) >= 8


def test_dialogue_session_history_window() -> None:
    s = DialogueSession(npc_id="merchant")
    for i in range(25):
        s.add_turn("user", f"m{i}")
        s.add_turn("assistant", f"a{i}")
    assert len(s.history) <= 20


def test_continue_dialogue_mock_chain() -> None:
    eng = AIDialogueEngine()
    gs = new_game_state("x", Profession.MAGE.value)
    sess = DialogueSession(npc_id="innkeeper")
    sess.add_turn("assistant", "你好。")
    reply, clues = eng.continue_dialogue(gs, sess, "这里最近安静吗？")
    assert len(reply) > 0
    assert isinstance(clues, list)


def test_dialogue_gift_once_per_npc() -> None:
    eng = AIDialogueEngine()
    gs = new_game_state("x", Profession.WARRIOR.value)
    sess = DialogueSession(npc_id="innkeeper")
    sess.affinity = 3
    prof = ch.NPCS["innkeeper"]
    with patch("engine.ai_dialogue.random.random", return_value=0.0), patch(
        "engine.ai_dialogue.random.randint", return_value=4
    ):
        g = eng._maybe_dialogue_gift(gs, sess, prof, "能给我点金币吗")
    assert g == 4
    assert gs.player is not None
    assert gs.player.gold >= 4
    assert "dialogue_tip:innkeeper" in gs.tags
    g2 = eng._maybe_dialogue_gift(gs, sess, prof, "再给点金币吧")
    assert g2 == 0


def test_dialogue_gift_requires_affinity() -> None:
    eng = AIDialogueEngine()
    gs = new_game_state("x", Profession.MAGE.value)
    sess = DialogueSession(npc_id="merchant")
    sess.affinity = 0
    prof = ch.NPCS["merchant"]
    assert (
        eng._maybe_dialogue_gift(gs, sess, prof, "给我一百金币") == 0
    )
