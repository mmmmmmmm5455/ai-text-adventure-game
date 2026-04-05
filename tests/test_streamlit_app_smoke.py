"""
Streamlit AppTest：整页脚本可执行（不替代人工 UI 走查）。

默认运行；若环境过旧或 CI 不稳定，可设 SKIP_STREAMLIT_APPTEST=1 跳过。
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.streamlit_app


@pytest.mark.skipif(
    os.environ.get("SKIP_STREAMLIT_APPTEST", "").lower() in ("1", "true", "yes"),
    reason="SKIP_STREAMLIT_APPTEST=1",
)
def test_streamlit_app_script_runs() -> None:
    pytest.importorskip("streamlit.testing.v1")
    from streamlit.testing.v1 import AppTest

    root = Path(__file__).resolve().parents[1]
    app_path = root / "frontend" / "app.py"
    assert app_path.is_file()
    at = AppTest.from_file(str(app_path), default_timeout=90)
    at.run(timeout=90)
    assert at.markdown or at.title or at.subheader
