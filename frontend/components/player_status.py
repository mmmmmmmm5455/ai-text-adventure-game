"""左侧玩家状态展示。"""

from __future__ import annotations

import streamlit as st

from core.i18n import t
from game.companion import get_active_companion
from game.game_state import GameState


def render_player_status(state: GameState) -> None:
    """渲染玩家状态面板。"""
    p = state.player
    if not p:
        st.info(t("status.no_player"))
        return
    st.subheader(t("status.character"))
    st.write(f"**{p.name}** · {p.profession.value} · {p.gender} · Lv.{p.level}")
    st.progress(min(1.0, p.hp / max(1, p.max_hp)), text=t("status.hp", v=p.hp, m=p.max_hp))
    st.progress(min(1.0, p.mp / max(1, p.max_mp)), text=t("status.mp", v=p.mp, m=p.max_mp))
    st.caption(t("status.gold_xp", gold=p.gold, xp=p.xp))
    st.caption(
        t("status.stats", str=p.strength, int=p.intelligence, agi=p.agility, cha=p.charisma)
    )
    st.divider()
    comp = get_active_companion(state)
    if comp:
        st.subheader(t("status.companion"))
        st.write(f"**{comp.get('name', '?')}**")
        st.caption(comp.get("special_skill", ""))
        st.caption(t("status.loyalty", v=int(comp.get("loyalty_score", 50))))
        st.caption(t("status.instinct"))
    st.divider()
    st.caption(t("status.location", loc=state.current_scene_id))
    st.caption(t("status.time_round", time=state.time_label(), round=state.round_count))
    st.divider()
    st.subheader(t("status.completed"))
    done = [q.name for q in state.quests.completed_quests()]
    if done:
        for n in done:
            st.write(f"- {n}")
    else:
        st.caption(t("status.none"))
