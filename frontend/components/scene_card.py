"""场景描述卡片。"""

from __future__ import annotations

import streamlit as st


def render_scene_card(title: str, body: str) -> None:
    st.markdown(
        f"""
<div class="scene-card">
  <div class="scene-title">{title}</div>
  <div class="scene-body">{body}</div>
</div>
        """,
        unsafe_allow_html=True,
    )
