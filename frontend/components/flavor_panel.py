"""传说与异象：预言书、报纸、梦境、骰子、占星、旋律、记忆、地图演变、礼物盒、虚空低语、成就。"""

from __future__ import annotations

import streamlit as st

from core.i18n import t
from engine.enhancement_engine import EnhancementEngine
from engine.story_engine import StoryEngine
from game.game_state import GameState
from utils.helpers import validate_user_text


def _flavor_engine(engine: StoryEngine) -> EnhancementEngine:
    try:
        return engine.flavor
    except AttributeError:
        # 旧版 @st.cache_resource 缓存的 StoryEngine 实例可能早于 flavor 属性
        if getattr(engine, "_flavor_eng", None) is None:
            engine._flavor_eng = EnhancementEngine()
        return engine._flavor_eng


def render_flavor_panel(gs: GameState, engine: StoryEngine) -> None:
    fe = _flavor_engine(engine)
    with st.expander(t("flavor.title"), expanded=False):
        st.caption(t("flavor.caption"))
        if gs.pending_gift_box:
            st.warning(t("flavor.gift.pending"))
            if st.button(t("flavor.gift.open"), key="open_gift_box"):
                with st.spinner(t("flavor.spinner.box")):
                    txt = fe.open_fate_gift_box(gs)
                st.session_state["flavor_last_output"] = txt
                st.rerun()

        c1, c2 = st.columns(2)
        with c1:
            if st.button(t("flavor.btn.prophecy"), key="flavor_prophecy"):
                if not gs.player or gs.player.gold < 5:
                    st.error(t("ui.not_enough_gold"))
                else:
                    gs.player.gold -= 5
                    with st.spinner(t("flavor.spinner.pages")):
                        st.session_state["flavor_last_output"] = fe.generate_prophecy(gs)
                    st.rerun()
        with c2:
            if st.button(t("flavor.btn.dice"), key="flavor_dice"):
                with st.spinner(t("flavor.spinner.dice")):
                    _roll, body = fe.generate_fate_dice(gs)
                    st.session_state["flavor_last_output"] = body
                st.rerun()

        c3, c4 = st.columns(2)
        with c3:
            if st.button(t("flavor.btn.paper"), key="flavor_paper"):
                if gs.current_scene_id not in ("tavern", "village_square"):
                    st.error(t("flavor.err.buy_place"))
                elif not gs.player or gs.player.gold < 3:
                    st.error(t("ui.not_enough_gold"))
                else:
                    gs.player.gold -= 3
                    gs.newspaper_issue = int(gs.newspaper_issue) + 1
                    with st.spinner(t("flavor.spinner.ink")):
                        st.session_state["flavor_last_output"] = fe.generate_newspaper(
                            gs, gs.newspaper_issue
                        )
                    gs.touch()
                    st.rerun()
        with c4:
            if st.button(t("flavor.btn.echo"), key="flavor_echo"):
                if not gs.player or gs.player.gold < 8:
                    st.error(t("ui.not_enough_gold"))
                else:
                    gs.player.gold -= 8
                    with st.spinner(t("flavor.spinner.echo")):
                        st.session_state["flavor_last_output"] = fe.generate_memory_echo(gs)
                    st.rerun()

        if st.button(t("flavor.btn.world"), key="flavor_world"):
            with st.spinner(t("flavor.spinner.world")):
                st.session_state["flavor_last_output"] = fe.generate_world_map_narrative(gs)
            st.rerun()

        st.divider()
        st.caption(t("flavor.cap.astro_melody"))
        astro = st.text_input(t("flavor.input.astro"), max_chars=120, key="flavor_astro_in")
        if st.button(t("flavor.btn.astro"), key="flavor_astro_go"):
            if not astro.strip():
                st.error(t("ui.please_enter"))
            else:
                ok, err = validate_user_text(astro)
                if not ok:
                    st.error(err)
                else:
                    with st.spinner(t("flavor.spinner.stars")):
                        st.session_state["flavor_last_output"] = fe.generate_astrology(gs, astro)
                    st.rerun()

        mel = st.text_input(t("flavor.input.melody"), max_chars=200, key="flavor_mel_in")
        if st.button(t("flavor.btn.melody"), key="flavor_mel_go"):
            if not mel.strip():
                st.error(t("flavor.error.hum"))
            else:
                ok, err = validate_user_text(mel)
                if not ok:
                    st.error(err)
                else:
                    with st.spinner(t("flavor.spinner.melody")):
                        st.session_state["flavor_last_output"] = fe.generate_melody_reading(gs, mel)
                    st.rerun()

        budget = int(getattr(gs, "meta_break_budget", 0))
        if st.button(
            t("flavor.btn.meta_left", n=budget),
            key="flavor_meta",
            disabled=budget <= 0,
        ):
            with st.spinner(t("flavor.spinner.meta")):
                out = fe.generate_meta_whisper(gs)
                st.session_state["flavor_last_output"] = out or t("flavor.meta.no_charges")
            st.rerun()

        out = st.session_state.get("flavor_last_output")
        if out:
            st.markdown("---")
            st.markdown(out)

        if gs.world_evolution:
            with st.expander(t("flavor.expander.world")):
                for line in gs.world_evolution[-5:]:
                    st.caption(line)
