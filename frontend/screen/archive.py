"""存档页：保存与读取。"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.config import get_settings
from core.exceptions import SaveLoadError
from core.i18n import t
from game.game_state import GameState


def save_path() -> Path:
    return get_settings().saves_dir / "slot1.json"


def render_archive(state: GameState | None) -> GameState | None:
    """返回加载后的状态（若成功）。"""
    st.subheader(t("archive.title"))
    p = save_path()
    st.caption(t("archive.slot", path=p))
    c1, c2 = st.columns(2)
    with c1:
        if st.button(t("archive.save")):
            if not state or not state.player:
                st.error(t("archive.no_state"))
            else:
                try:
                    state.save(p)
                    st.success(t("archive.saved"))
                except SaveLoadError as e:
                    st.error(str(e))
    with c2:
        if st.button(t("archive.load")):
            try:
                if not p.exists():
                    st.warning(t("archive.no_file"))
                    return state
                loaded = GameState.load(p)
                st.success(t("archive.loaded"))
                return loaded
            except SaveLoadError as e:
                st.error(str(e))
    return state
