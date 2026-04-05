"""探索模式选择按钮。"""

from __future__ import annotations

import streamlit as st

from engine.story_engine import ChoiceOption


def render_choices(choices: list[ChoiceOption], key_prefix: str) -> str | None:
    """
    渲染选项按钮，返回被选中的 choice_id；若未选择则返回 None。
    使用 session 暂存选择结果。
    """
    picked = st.session_state.get(f"{key_prefix}_picked")
    cols = st.columns(2)
    for i, ch in enumerate(choices):
        with cols[i % 2]:
            if st.button(ch.label, key=f"{key_prefix}_btn_{ch.choice_id}"):
                st.session_state[f"{key_prefix}_picked"] = ch.choice_id
                picked = ch.choice_id
    return picked
