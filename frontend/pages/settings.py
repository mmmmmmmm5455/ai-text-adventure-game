"""设置页：模型与说明。"""

from __future__ import annotations

import streamlit as st

from core.config import get_settings


def render_settings() -> None:
    s = get_settings()
    st.subheader("设置")
    st.caption("模型与地址通过环境变量或 `.env` 配置，修改后需重启应用。")
    st.write(f"- Ollama 地址：`{s.ollama_base_url}`")
    st.write(f"- 对话模型：`{s.ollama_model}`")
    st.write(f"- 嵌入模型：`{s.ollama_embed_model}`")
    st.write(f"- 超时（秒）：{s.ollama_timeout}")
