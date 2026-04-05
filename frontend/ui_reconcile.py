"""
根据已恢复的 GameState 校正 Streamlit session 中的 ui_mode / 对话会话一致性。
减轻：读档后仍停在「创建角色」页、或 ui_mode 与 dialogue_session 互斥等漂移。
"""

from __future__ import annotations

from typing import Any, MutableMapping


def reconcile_streamlit_ui_state(
    session: MutableMapping[str, Any],
    *,
    has_game_state: bool,
) -> None:
    """
    has_game_state：当前是否已有玩家存档对象（非 None）。
    规则：
    - 有存档且 ui_mode 仍为 home → 改为 explore（避免读档后卡在创建页）
    - 有 dialogue_session 但 ui_mode 不是 dialogue → 切到 dialogue
    - ui_mode 是 dialogue 但无 dialogue_session → 回 explore
    - settings 模式不改动
    """
    if not has_game_state:
        return
    if session.get("ui_mode") == "settings":
        return
    if session.get("ui_mode") == "home":
        session["ui_mode"] = "explore"

    has_sess = session.get("dialogue_session") is not None
    mode = session.get("ui_mode")
    if has_sess and mode != "dialogue":
        session["ui_mode"] = "dialogue"
    elif not has_sess and mode == "dialogue":
        session["ui_mode"] = "explore"
