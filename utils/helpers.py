"""通用辅助函数。"""

from __future__ import annotations

from core.config import get_settings


def validate_user_text(text: str) -> tuple[bool, str]:
    """校验用户输入长度，返回 (是否通过, 错误信息)。"""
    s = text.strip()
    if not s:
        return False, "输入不能为空。"
    max_len = get_settings().max_user_input_length
    if len(s) > max_len:
        return False, f"输入过长（上限 {max_len} 字）。"
    return True, ""
