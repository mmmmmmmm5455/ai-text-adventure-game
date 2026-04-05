"""设置页：模型与说明。"""

from __future__ import annotations

import streamlit as st

from core.config import get_settings
from core.i18n import t
from frontend.narrative_language_ui import render_narrative_language_picker


def render_settings() -> None:
    s = get_settings()
    st.subheader(t("settings.title"))
    render_narrative_language_picker()
    st.divider()
    st.caption(t("settings.caption"))
    st.write(f"- {t('settings.ollama_url')}：`{s.ollama_base_url}`")
    st.write(f"- {t('settings.chat_model')}：`{s.ollama_model}`")
    st.write(f"- {t('settings.embed_model')}：`{s.ollama_embed_model}`")
    st.write(f"- {t('settings.timeout')}：{s.ollama_timeout}")
