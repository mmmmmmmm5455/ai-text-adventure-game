"""首页：角色创建。"""

from __future__ import annotations

import streamlit as st

from game.constants import PROFESSION_KEYS


def render_home() -> tuple[str | None, str | None]:
    """
    返回 (角色名, 职业) 若点击开始；否则 (None, None)。
    """
    st.subheader("创建角色")
    name = st.text_input("角色名", max_chars=32, placeholder="例如：艾琳")
    prof = st.selectbox("职业", list(PROFESSION_KEYS))
    if st.button("开始冒险", type="primary"):
        if not name or not name.strip():
            st.error("请输入角色名。")
            return None, None
        return name.strip(), prof
    return None, None
