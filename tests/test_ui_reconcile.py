"""Streamlit UI 与 game_state 同步逻辑（无 Streamlit 运行时）。"""

from __future__ import annotations

from frontend.ui_reconcile import reconcile_streamlit_ui_state


def test_reconcile_home_to_explore_when_save_present() -> None:
    sess: dict = {"ui_mode": "home", "game_state": object(), "dialogue_session": None}
    reconcile_streamlit_ui_state(sess, has_game_state=True)
    assert sess["ui_mode"] == "explore"


def test_reconcile_settings_unchanged() -> None:
    sess: dict = {"ui_mode": "settings", "dialogue_session": None}
    reconcile_streamlit_ui_state(sess, has_game_state=True)
    assert sess["ui_mode"] == "settings"


def test_reconcile_dialogue_session_forces_dialogue_mode() -> None:
    sess: dict = {"ui_mode": "explore", "dialogue_session": object()}
    reconcile_streamlit_ui_state(sess, has_game_state=True)
    assert sess["ui_mode"] == "dialogue"


def test_reconcile_dialogue_mode_without_session_back_to_explore() -> None:
    sess: dict = {"ui_mode": "dialogue", "dialogue_session": None}
    reconcile_streamlit_ui_state(sess, has_game_state=True)
    assert sess["ui_mode"] == "explore"


def test_reconcile_no_game_state_no_op() -> None:
    sess: dict = {"ui_mode": "home"}
    reconcile_streamlit_ui_state(sess, has_game_state=False)
    assert sess["ui_mode"] == "home"
