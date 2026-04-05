"""对话引擎测试。"""

from __future__ import annotations

from engine.ai_dialogue import AIDialogueEngine, DialogueSession
from game.player import Profession
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
