"""
標準輸入輸出編碼：避免 Windows 主控台預設 cp950 導致中文 print / loguru 崩潰。
"""

from __future__ import annotations

import sys


def configure_stdio_utf8() -> None:
    """在 Windows 上盡量將 stdout/stderr 設為 UTF-8，失敗則忽略。"""
    if sys.platform != "win32":
        return
    for stream in (sys.stdout, sys.stderr):
        if stream is None:
            continue
        reconf = getattr(stream, "reconfigure", None)
        if callable(reconf):
            try:
                reconf(encoding="utf-8", errors="replace")
            except (OSError, ValueError, TypeError, AttributeError):
                pass
