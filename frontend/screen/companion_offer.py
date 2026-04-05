"""待招募队友卡片（接受 / 谢绝）。"""

from __future__ import annotations

import streamlit as st

from core.i18n import t
from engine.story_engine import StoryEngine, accept_companion_offer, decline_companion_offer
from game.companion import JOIN_GOLD_COST
from game.game_state import GameState


def render_companion_offer(gs: GameState, engine: StoryEngine) -> None:
    offer = gs.pending_companion_offer
    if not offer:
        return
    st.subheader(t("companion_offer.title"))
    st.markdown(f"**{offer.get('name', t('companion_offer.nameless'))}**")
    st.caption(offer.get("avatar_desc", ""))
    st.write(f"**{t('companion_offer.personality')}：** {offer.get('personality', '')}")
    st.write(f"**{t('companion_offer.join_condition')}：** {offer.get('join_condition', '')}")
    st.write(f"**{t('companion_offer.special_skill')}：** {offer.get('special_skill', '')}")
    st.caption(f"{t('companion_offer.clue_prefix')}: {offer.get('hidden_trait_clue', '...')}")
    gold = gs.player.gold if gs.player else 0
    st.caption(t("companion_offer.pay_caption", cost=JOIN_GOLD_COST, gold=gold))
    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            t("companion_offer.btn.accept"),
            type="primary",
            key="companion_accept_btn",
            disabled=gold < JOIN_GOLD_COST,
        ):
            with st.spinner(t("companion_offer.spinner.accept")):
                accept_companion_offer(engine, gs)
            st.rerun()
    with c2:
        if st.button(t("companion_offer.btn.decline"), key="companion_decline_btn"):
            decline_companion_offer(gs)
            st.rerun()
