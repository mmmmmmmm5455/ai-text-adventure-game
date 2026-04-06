"""Pytest 全局钩子：Windows 終端 UTF-8，避免中文輸出 UnicodeEncodeError。"""

from __future__ import annotations

from core.io_encoding import configure_stdio_utf8


def pytest_configure(config: object) -> None:  # noqa: ARG001
    configure_stdio_utf8()
