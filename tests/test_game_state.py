"""游戏状态与存档测试。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.exceptions import SaveLoadError
from game.game_state import GameState
from game.player import Profession
from story.world_config import new_game_state


def test_game_state_round_and_time(tmp_path: Path) -> None:
    gs = new_game_state("测试英雄", Profession.WARRIOR.value)
    assert gs.time_label() in ("早晨", "正午", "黄昏", "深夜")
    for _ in range(5):
        gs.advance_round()
    assert gs.round_count == 5


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    gs = new_game_state("存档", Profession.MAGE.value)
    p = tmp_path / "t.json"
    gs.save(p)
    raw = json.loads(p.read_text(encoding="utf-8"))
    assert raw.get("schema_version") >= 1
    assert "story_asset_version" in raw
    gs2 = GameState.load(p)
    assert gs2.player and gs2.player.name == "存档"
    assert gs2.current_scene_id == gs.current_scene_id


def test_load_missing_file(tmp_path: Path) -> None:
    with pytest.raises(SaveLoadError):
        GameState.load(tmp_path / "nope.json")
