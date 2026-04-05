"""对话模式聊天区。"""

from __future__ import annotations

import streamlit as st


def render_chat_history(messages: list[tuple[str, str]]) -> None:
    """messages: (role, content) role in user/assistant"""
    for role, content in messages:
        with st.chat_message("user" if role == "user" else "assistant"):
            st.write(content)
