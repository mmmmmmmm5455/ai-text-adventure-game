"""叙事语言选择：与 core.narrative_language 同步。"""

from __future__ import annotations

import streamlit as st

from core.i18n import t
from core.narrative_language import get_narrative_language, language_label, set_narrative_language


def render_narrative_language_picker() -> None:
    """在首页或设置页展示；切换后立即 rerun 并更新全局叙事语言。"""
    cur = st.session_state.get("narrative_language", "zh")
    opts = ["zh", "en"]
    ix = opts.index(cur) if cur in opts else 0
    lang = get_narrative_language()
    choice = st.selectbox(
        t("lang.picker"),
        opts,
        index=ix,
        format_func=lambda c: f"{language_label(c)} ({c})",
        key=f"narrative_language_picker_{lang}",
    )
    if choice != cur:
        st.session_state["narrative_language"] = choice
        set_narrative_language(choice)
        st.rerun()
