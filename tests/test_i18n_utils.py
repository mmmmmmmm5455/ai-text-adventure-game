"""i18n key 资源与格式化行为。"""

from __future__ import annotations

from core.i18n import t
from core.narrative_language import set_narrative_language


def teardown_function() -> None:
    set_narrative_language("zh")


def test_i18n_basic_switch() -> None:
    set_narrative_language("zh")
    assert t("ui.not_enough_gold") == "金币不足。"
    set_narrative_language("en")
    assert t("ui.not_enough_gold") == "Not enough gold."


def test_i18n_formatting() -> None:
    set_narrative_language("zh")
    assert "雷恩" in t("dialogue.safe", name="雷恩")
    set_narrative_language("en")
    assert "Rein" in t("dialogue.safe", name="Rein")


def test_i18n_progress_and_labels() -> None:
    set_narrative_language("zh")
    assert "目标进度" in t("quest.progress", progress=1, total=3, objs="A / B / C")
    assert "新游戏" in t("app.new_game")
    set_narrative_language("en")
    assert "Progress" in t("quest.progress", progress=1, total=3, objs="A / B / C")
    assert t("app.new_game") == "New Game"
