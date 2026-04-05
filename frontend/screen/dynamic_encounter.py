"""动态广场路人遭遇界面。"""

from __future__ import annotations

import streamlit as st

from core.i18n import t
from game.dynamic_npc import check_hidden_bonus, register_dynamic_npc_quest
from game.game_state import GameState


def render_dynamic_npc_encounter(gs: GameState) -> None:
    """渲染当前 active_dynamic_npc_id 对应路人；按钮内直接修改 gs 并 rerun。"""
    nid = gs.active_dynamic_npc_id
    if not nid:
        return
    npc = next((n for n in gs.dynamic_npcs if n.get("id") == nid), None)
    if not npc:
        gs.active_dynamic_npc_id = None
        gs.touch()
        return

    st.subheader(f"{t('dyn.title')} · {npc.get('name', t('dyn.unknown'))}")
    st.markdown(f"*{npc.get('appearance', '')}*")
    st.caption(f"{t('dyn.personality')}：{npc.get('personality', '')}")
    if npc.get("linked_blurb"):
        st.info(npc["linked_blurb"])

    tier_label = {"common": t("dyn.common"), "rare": t("dyn.rare"), "epic": t("dyn.epic")}.get(
        npc.get("tier", "common"),
        t("dyn.common"),
    )
    st.caption(f"{t('dyn.tier')}：{tier_label}　{t('dyn.mood')}：{int(npc.get('mood', 50))}/100")

    phase = npc.get("interaction_phase", "opening")

    if phase == "opening":
        st.write(f"**{t('dyn.begin')}：**「{npc.get('opening', '...')}」")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(t("dyn.btn.details"), key=f"dyn_detail_{nid}"):
                npc["interaction_phase"] = "detail"
                npc["mood"] = min(100, int(npc.get("mood", 50)) + 3)
                gs.touch()
                st.rerun()
        with c2:
            if st.button(t("dyn.btn.tip"), key=f"dyn_tip_{nid}"):
                if not gs.player or gs.player.gold < 5:
                    st.warning(t("ui.not_enough_gold"))
                else:
                    gs.player.gold -= 5
                    npc["mood"] = min(100, int(npc.get("mood", 50)) + 12)
                    gs.add_log(t("dyn.log.tip"))
                    gs.touch()
                    st.rerun()
        with c3:
            if st.button(t("dyn.btn.leave"), key=f"dyn_leave_{nid}"):
                gs.dynamic_npcs = [n for n in gs.dynamic_npcs if n.get("id") != nid]
                gs.active_dynamic_npc_id = None
                gs.add_log(t("dyn.log.leave", name=npc.get("name", t("dyn.title"))))
                gs.touch()
                st.rerun()

    elif phase == "detail":
        st.write(f"**{t('dyn.request')}：**")
        st.write(npc.get("request", ""))
        st.caption(
            t(
                "dyn.progress_help",
                p=int(npc.get("progress", 0)),
                n=int(npc.get("objective_count", 1)),
            )
        )
        a1, a2 = st.columns(2)
        with a1:
            if st.button(t("dyn.btn.accept"), key=f"dyn_accept_{nid}"):
                npc["status"] = "active"
                npc["interaction_phase"] = "accepted"
                register_dynamic_npc_quest(gs, npc)
                if gs.player and check_hidden_bonus(
                    gs.player.equipped_weapon_id,
                    gs.player.equipped_armor_id,
                    str(npc.get("hidden_trigger", "none")),
                ):
                    npc["hidden_bonus_applied"] = True
                    gs.add_log(t("dyn.log.hidden_bonus"))
                gs.active_dynamic_npc_id = None
                gs.add_log(t("dyn.log.accept", name=npc.get("name", t("dyn.title"))))
                gs.touch()
                st.rerun()
        with a2:
            if st.button(t("dyn.btn.decline"), key=f"dyn_decline_{nid}"):
                gs.dynamic_npcs = [n for n in gs.dynamic_npcs if n.get("id") != nid]
                gs.active_dynamic_npc_id = None
                gs.add_log(t("dyn.log.decline", name=npc.get("name", t("dyn.title"))))
                gs.touch()
                st.rerun()

    st.divider()
    if st.button(
        t("dyn.btn.later"),
        key=f"dyn_later_{nid}",
    ):
        gs.active_dynamic_npc_id = None
        gs.touch()
        st.rerun()
