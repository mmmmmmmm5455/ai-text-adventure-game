"""文本处理：截断、清洗。"""

from __future__ import annotations


def clamp_text(text: str, max_len: int) -> str:
    t = text.strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"
