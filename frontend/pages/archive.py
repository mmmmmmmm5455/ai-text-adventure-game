"""存档页：保存与读取。"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.config import get_settings
from core.exceptions import SaveLoadError
from game.game_state import GameState


def save_path() -> Path:
    return get_settings().saves_dir / "slot1.json"


def render_archive(state: GameState | None) -> GameState | None:
    """返回加载后的状态（若成功）。"""
    st.subheader("存档")
    p = save_path()
    st.caption(f"当前存档位：`{p}`")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("保存游戏"):
            if not state or not state.player:
                st.error("没有可保存的游戏。")
            else:
                try:
                    state.save(p)
                    st.success("已保存。")
                except SaveLoadError as e:
                    st.error(str(e))
    with c2:
        if st.button("读取游戏"):
            try:
                if not p.exists():
                    st.warning("存档文件不存在。")
                    return state
                loaded = GameState.load(p)
                st.success("已读取存档。")
                return loaded
            except SaveLoadError as e:
                st.error(str(e))
    return state
