"""关键静态文本的中英切换回归。"""

from __future__ import annotations

from core.narrative_language import set_narrative_language
from game.player import Profession
from story.endings import decide_ending
from story.quests import default_quests
from story.scenes import scene_description, scene_name
from story.world_config import get_world_lore, get_world_name, new_game_state


def teardown_function() -> None:
    set_narrative_language("zh")


def test_world_text_switch_to_english() -> None:
    set_narrative_language("en")
    assert "Village" in get_world_name()
    assert "medieval village" in get_world_lore()


def test_default_quests_switch_to_english() -> None:
    set_narrative_language("en")
    qs = default_quests()
    names = [q.name for q in qs]
    assert "Investigate Forest Anomalies" in names
    q0 = qs[0]
    assert any("Enter" in obj for obj in q0.objectives)


def test_scene_name_and_description_switch_to_english() -> None:
    set_narrative_language("en")
    assert scene_name("village_square") == "Village Square"
    assert "stone square" in scene_description("village_square")


def test_ending_title_switch_to_english() -> None:
    set_narrative_language("en")
    gs = new_game_state("Tester", Profession.WARRIOR.value)
    info = decide_ending(gs)
    assert "Ending" in info.title
