"""左侧玩家状态展示。"""

from __future__ import annotations

import streamlit as st

from game.game_state import GameState


def render_player_status(state: GameState) -> None:
    """渲染玩家状态面板。"""
    p = state.player
    if not p:
        st.info("尚未创建角色。")
        return
    st.subheader("角色")
    st.write(f"**{p.name}** · {p.profession.value} · Lv.{p.level}")
    st.progress(min(1.0, p.hp / max(1, p.max_hp)), text=f"生命 {p.hp}/{p.max_hp}")
    st.progress(min(1.0, p.mp / max(1, p.max_mp)), text=f"能量 {p.mp}/{p.max_mp}")
    st.caption(f"金币：{p.gold}　经验：{p.xp}")
    st.caption(f"力量 {p.strength} · 智力 {p.intelligence} · 敏捷 {p.agility} · 魅力 {p.charisma}")
    st.divider()
    st.caption(f"位置：{state.current_scene_id}")
    st.caption(f"时间：{state.time_label()}　回合：{state.round_count}")
    st.divider()
    st.subheader("已完成任务")
    done = [q.name for q in state.quests.completed_quests()]
    if done:
        for n in done:
            st.write(f"- {n}")
    else:
        st.caption("暂无")
