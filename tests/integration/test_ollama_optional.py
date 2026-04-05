"""
可选集成：真实 Ollama。默认跳过；设置环境变量 RUN_LLM_INTEGRATION=1 时运行。

用法（本机已启动 Ollama 且已 pull 模型）:
  set RUN_LLM_INTEGRATION=1
  pytest tests/integration/test_ollama_optional.py -v --tb=short
"""

from __future__ import annotations

import os

import pytest

from engine.llm_client import LLMClient


pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not os.environ.get("RUN_LLM_INTEGRATION"),
    reason="设置 RUN_LLM_INTEGRATION=1 以启用真实 Ollama 调用",
)
def test_ollama_generate_short_line() -> None:
    llm = LLMClient()
    assert llm.health_check() is True
    text = llm.generate_text(
        "用一句话描述一口中世纪村庄的老井。",
        system="只输出中文一句，不要解释。",
        temperature=0.3,
        max_tokens=80,
    )
    assert len(text.strip()) >= 4
    assert "（离线模式）" not in text
