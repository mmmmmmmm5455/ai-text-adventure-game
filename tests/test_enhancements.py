"""风味事件与计数。"""

from __future__ import annotations

from game.enhancements import bump_counter, record_flavor_event
from game.player import Profession
from story.world_config import new_game_state


def test_bump_and_flavor_log() -> None:
    gs = new_game_state("x", Profession.WARRIOR.value)
    assert bump_counter(gs, "searches", 1) == 1
    record_flavor_event(gs, "test", "hello")
    assert gs.flavor_log[-1]["kind"] == "test"
