"""存档页：保存与读取。"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.config import get_settings
from core.exceptions import SaveLoadError
from core.i18n import t
from database.possession_db import possession_backend_ready
from game.game_state import GameState
from game.possession_bridge import resolve_possession_player_id, upload_snapshot_from_game_state


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

    if possession_backend_ready():
        with st.expander(t("archive.possession_expander"), expanded=False):
            st.caption(t("archive.possession_hint"))
            pid_raw = st.text_input(t("archive.possession_player_id"), key="possession_player_uuid")
            with_llm = st.checkbox(t("archive.possession_last_words_llm"), value=False)
            if st.button(t("archive.possession_upload")):
                if not state or not state.player:
                    st.error(t("archive.no_state"))
                else:
                    pid = resolve_possession_player_id(pid_raw or None)
                    if pid is None:
                        st.error(t("archive.possession_bad_uuid"))
                    else:
                        llm = None
                        if with_llm:
                            from engine.llm_client import LLMClient

                            llm = LLMClient()
                        sid = upload_snapshot_from_game_state(
                            pid,
                            state,
                            label=t("archive.possession_label_default"),
                            generate_last_words_llm=llm,
                        )
                        if sid is None:
                            st.error(t("archive.possession_failed"))
                        else:
                            st.success(t("archive.possession_uploaded", snapshot_id=str(sid)))
    return state
