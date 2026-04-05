"""任务列表。"""

from __future__ import annotations

import streamlit as st

from core.i18n import t
from game.game_state import GameState


def render_quest_list(state: GameState) -> None:
    st.subheader(t("quest.active"))
    active = state.quests.active_quests()
    if not active:
        st.caption(t("status.none"))
        return
    for q in active:
        kind_label = t("quest.main") if q.kind.value == "主线" else t("quest.side")
        st.write(f"**{q.name}** ({kind_label})")
        st.caption(q.description)
        objs = " / ".join(q.objectives) if q.objectives else ""
        st.caption(t("quest.progress", progress=q.progress, total=max(1, len(q.objectives)), objs=objs))
