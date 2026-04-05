"""故事引擎测试（Mock LLM，不依赖 Ollama）。"""

from __future__ import annotations

from unittest.mock import patch

from engine.story_engine import StoryEngine
from game.player import Profession
from story.world_config import new_game_state


def test_fallback_scene_description() -> None:
    se = StoryEngine()
    gs = new_game_state("旅人", Profession.BARD.value)
    with patch.object(se.llm, "generate_text", side_effect=RuntimeError("no ollama")):
        txt = se._static_scene_fallback(gs.current_scene_id)
        assert "村庄" in txt or "广场" in txt


def test_process_move_and_search() -> None:
    se = StoryEngine()
    gs = new_game_state("旅人", Profession.MAGE.value)
    msg, talk = se.process_choice(gs, "move:misty_forest")
    assert not talk
    assert gs.current_scene_id == "misty_forest"
