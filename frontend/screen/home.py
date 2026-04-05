"""首页：角色创建。"""

from __future__ import annotations

import streamlit as st

from core.i18n import t
from frontend.narrative_language_ui import render_narrative_language_picker
from game.constants import PROFESSION_KEYS


def render_home() -> tuple[str | None, str | None, str | None]:
    """
    返回 (角色名, 职业, 性别认同) 若点击开始；否则全为 None。
    """
    render_narrative_language_picker()
    st.divider()
    st.subheader(t("home.create"))
    name = st.text_input(
        t("home.name"),
        max_chars=32,
        placeholder=t("home.name_ph"),
    )
    prof = st.selectbox(t("home.profession"), list(PROFESSION_KEYS))
    st.caption(t("home.gender_caption"))
    gender_mode = st.radio(
        t("home.gender"),
        [t("home.gender_male"), t("home.gender_female"), t("home.gender_custom")],
        horizontal=True,
    )
    custom_gender = ""
    if gender_mode == t("home.gender_custom"):
        custom_gender = st.text_input(
            t("home.custom"),
            max_chars=32,
            placeholder=t("home.custom_ph"),
        )
    if st.button(t("home.start"), type="primary"):
        if not name or not name.strip():
            st.error(t("home.err_name"))
            return None, None, None
        if gender_mode == t("home.gender_custom"):
            if not custom_gender or not custom_gender.strip():
                st.error(t("home.err_custom"))
                return None, None, None
            g = custom_gender.strip()[:32]
        else:
            g = gender_mode
        return name.strip(), prof, g
    return None, None, None
