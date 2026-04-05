"""任务列表。"""

from __future__ import annotations

import streamlit as st

from game.game_state import GameState


def render_quest_list(state: GameState) -> None:
    st.subheader("进行中任务")
    active = state.quests.active_quests()
    if not active:
        st.caption("暂无")
        return
    for q in active:
        st.write(f"**{q.name}**（{q.kind.value}）")
        st.caption(q.description)
        objs = " / ".join(q.objectives) if q.objectives else ""
        st.caption(f"目标进度：{q.progress}/{max(1, len(q.objectives))} {objs}")
