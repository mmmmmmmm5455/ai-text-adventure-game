"""
Streamlit 主入口：三栏布局、探索与对话模式、存档。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 保证从仓库根目录导入包
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.io_encoding import configure_stdio_utf8

configure_stdio_utf8()

import streamlit as st

from core.i18n import t
from core.logger import setup_logging
from core.narrative_language import set_narrative_language
from engine.ai_dialogue import AIDialogueEngine, DialogueSession
from engine.event_handler import maybe_trigger_event
from engine.story_engine import (
    StoryEngine,
    accept_companion_offer,
    decline_companion_offer,
    grant_starting_items,
)
from frontend.components.chat import render_chat_history
from frontend.components.flavor_panel import render_flavor_panel
from frontend.components.player_status import render_player_status
from frontend.components.quest_list import render_quest_list
from frontend.components.scene_card import render_scene_card
from frontend.screen.archive import render_archive, save_path
from frontend.screen.companion_offer import render_companion_offer
from frontend.screen.dynamic_encounter import render_dynamic_npc_encounter
from frontend.screen.home import render_home
from frontend.screen.settings import render_settings
from frontend.ui_reconcile import reconcile_streamlit_ui_state
from game.gear_social_cues import gear_public_impression
from game.repair_system import durability_text
from story.world_config import get_world_lore, get_world_name, new_game_state
from utils.helpers import validate_user_text


@st.cache_resource
def get_engine(_cache_v: int = 2) -> StoryEngine:
    """_cache_v 仅用于在 StoryEngine API 变更时使 @st.cache_resource 失效。"""
    return StoryEngine()


@st.cache_resource
def get_dialogue_engine() -> AIDialogueEngine:
    """对话在 AIDialogueEngine 中实现，与 StoryEngine 分离。"""
    return AIDialogueEngine()


def _inject_css() -> None:
    st.markdown(
        """
<style>
  .stApp {
    background: linear-gradient(135deg, #1e1038 0%, #2d1b4e 40%, #1a3a52 100%);
    color: #f4f0ff;
  }
  .scene-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 14px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(6px);
  }
  .scene-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; }
  .scene-body { line-height: 1.7; white-space: pre-wrap; }
  div[data-testid="stSidebar"] { background-color: rgba(10,8,20,0.85); }
</style>
        """,
        unsafe_allow_html=True,
    )


def _init_session() -> None:
    defaults = {
        "game_state": None,
        "ui_mode": "home",
        "scene_text": "",
        "dialogue_session": None,
        "pending_dialogue_npc": None,
        "ollama_ok": None,
        "narrative_language": "zh",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def main() -> None:
    st.set_page_config(
        page_title=f"{get_world_name()} · {t('app.engine_caption')}",
        layout="wide",
    )
    setup_logging()
    _inject_css()
    _init_session()
    set_narrative_language(st.session_state.get("narrative_language", "zh"))
    reconcile_streamlit_ui_state(
        st.session_state,
        has_game_state=st.session_state.get("game_state") is not None,
    )
    engine = get_engine()
    dialogue_engine = get_dialogue_engine()

    with st.sidebar:
        st.title(get_world_name())
        st.caption(t("app.engine_caption"))
        if st.button(t("app.new_game")):
            st.session_state.game_state = None
            st.session_state.ui_mode = "home"
            st.session_state.scene_text = ""
            st.session_state.dialogue_session = None
            st.session_state.pending_dialogue_npc = None
            st.session_state.pop("ending_text", None)
            st.rerun()

        st.divider()
        st.session_state.game_state = render_archive(st.session_state.game_state)
        reconcile_streamlit_ui_state(
            st.session_state,
            has_game_state=st.session_state.game_state is not None,
        )

        if st.button(t("app.settings_btn")):
            st.session_state.ui_mode = "settings"
            st.rerun()

        st.divider()
        st.caption(t("app.help_tip"))

    gs = st.session_state.game_state

    left, mid, right = st.columns([1.1, 2.2, 1.1])

    with left:
        if gs:
            render_player_status(gs)

    with right:
        if gs:
            st.subheader(t("app.adventure_log"))
            for line in gs.game_log[-12:]:
                st.caption(line)
            st.divider()
            st.subheader(t("app.inventory"))
            if gs.player:
                for it in gs.player.inventory.items:
                    dur = durability_text(it)
                    tail = f" · {dur}" if dur else ""
                    st.write(f"- {it.name} x{it.quantity}{tail}")
            st.divider()
            render_quest_list(gs)

    with mid:
        if st.session_state.ui_mode == "settings":
            render_settings()
            if st.button(t("app.back")):
                st.session_state.ui_mode = "explore" if gs else "home"
                st.rerun()
            return

        if st.session_state.ui_mode == "home" or gs is None:
            st.markdown(f"### {get_world_name()}")
            st.write(get_world_lore())
            name, prof, gender = render_home()
            if name and prof and gender:
                with st.spinner(t("app.init_world")):
                    ngs = new_game_state(name, prof, gender)
                    grant_starting_items(ngs)
                    try:
                        ok = engine.llm.health_check()
                        st.session_state.ollama_ok = ok
                    except Exception:
                        st.session_state.ollama_ok = False
                    txt = engine.generate_scene_description(ngs)
                    ngs.add_log(t("app.adventure_begins"))
                    st.session_state.game_state = ngs
                    st.session_state.scene_text = txt
                    st.session_state.ui_mode = "explore"
                    st.rerun()
            return

        assert gs is not None

        if gs.active_dynamic_npc_id:
            render_dynamic_npc_encounter(gs)
            return

        if st.session_state.ui_mode == "dialogue" and st.session_state.dialogue_session:
            sess: DialogueSession = st.session_state.dialogue_session
            st.subheader(t("app.dialogue_title"))
            st.caption(t("app.dialogue_caption"))
            if gs.player:
                st.caption(
                    f"**{t('app.visible_equipment')}：** "
                    f"{gs.player.visible_equipment_for_npc()}"
                )
            msgs = [(r, c) for r, c in sess.history]
            render_chat_history(msgs)
            user_in = st.chat_input(t("app.chat_input"))
            if user_in:
                ok, err = validate_user_text(user_in)
                if not ok:
                    st.error(err)
                else:
                    with st.spinner(t("app.spinner.npc_thinking")):
                        reply, _clues = dialogue_engine.continue_dialogue(gs, sess, user_in)
                        gs.add_log(f"对话：{reply[:80]}…" if len(reply) > 80 else f"对话：{reply}")
                    st.rerun()
            a1, a2 = st.columns(2)
            with a1:
                if st.button(t("app.btn.show_gear")):
                    line = t("app.show_gear.line")
                    gs.add_log(
                        t("app.show_gear.log", gear=gear_public_impression(gs.player))
                        if gs.player
                        else t("app.show_gear.fallback")
                    )
                    with st.spinner(t("app.spinner.npc_reacting")):
                        reply, _ = dialogue_engine.continue_dialogue(gs, sess, line)
                        gs.add_log(f"亮出装备：{reply[:60]}…" if len(reply) > 60 else f"亮出装备：{reply}")
                    st.rerun()
            with a2:
                if st.button(t("app.btn.intimidate")):
                    with st.spinner(t("app.spinner.resolving")):
                        msg, got = dialogue_engine.try_intimidate(gs, sess)
                        if got:
                            st.success(t("app.gained_gold", n=got))
                        gs.add_log(msg[:100])
                    st.rerun()
            c1, c2 = st.columns(2)
            with c1:
                if st.button(t("app.btn.end_dialogue")):
                    closing = dialogue_engine.end_dialogue(gs, sess)
                    gs.add_log(closing)
                    st.session_state.dialogue_session = None
                    st.session_state.ui_mode = "explore"
                    st.rerun()
            with c2:
                if st.button(t("app.btn.refresh_scene")):
                    with st.spinner(t("app.spinner.generate_scene")):
                        st.session_state.scene_text = engine.generate_scene_description(gs)
                    st.rerun()
            return

        st.subheader(t("app.explore_title"))
        if st.session_state.ollama_ok is False:
            st.info(t("app.ollama_offline"))

        if gs.pending_companion_offer:
            render_companion_offer(gs, engine)
            st.divider()

        render_flavor_panel(gs, engine)

        render_scene_card(
            t("app.scene_title"),
            st.session_state.scene_text or t("app.scene_placeholder"),
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(t("app.btn.refresh_scene")):
                with st.spinner(t("app.spinner.generating")):
                    st.session_state.scene_text = engine.generate_scene_description(gs)
                st.rerun()
        with c2:
            if st.button(t("app.btn.random_event")):
                ev = maybe_trigger_event(gs)
                if ev:
                    gs.add_log(ev.message)
                st.rerun()
        with c3:
            if st.button(t("app.btn.long_ending")):
                with st.spinner(t("app.spinner.write_ending")):
                    st.session_state["ending_text"] = engine.generate_ending_narrative(gs)
                st.rerun()

        if "ending_text" in st.session_state and st.session_state["ending_text"]:
            st.success(st.session_state["ending_text"])

        st.divider()
        st.caption(t("app.choose_action"))
        choices = engine.generate_choices(gs)
        for ch in choices:
            if st.button(ch.label, key=f"ch_{ch.choice_id.replace(':', '_')}"):
                spin = t("app.spinner.processing")
                if ch.choice_id == "dyn_spawn":
                    spin = t("app.spinner.gen_passerby")
                elif ch.choice_id == "companion_seek":
                    spin = t("app.spinner.gen_companion")
                elif ch.choice_id == "companion_probe":
                    spin = t("app.spinner.gen_probe")
                with st.spinner(spin):
                    msg, enter_talk = engine.process_choice(gs, ch.choice_id)
                if ch.choice_id not in ("dyn_spawn", "companion_seek", "companion_probe"):
                    gs.add_log(msg[:120])
                elif ch.choice_id in ("companion_seek", "companion_probe"):
                    gs.add_log(msg[:160])
                if ch.choice_id == "dyn_spawn":
                    st.session_state.scene_text = msg
                elif ch.choice_id == "companion_seek":
                    st.session_state.scene_text = msg
                elif ch.choice_id == "companion_probe":
                    st.session_state.scene_text = msg
                if enter_talk and ch.choice_id.startswith("talk:"):
                    npc_id = ch.choice_id.split(":", 1)[1]
                    st.session_state.dialogue_session = DialogueSession(npc_id=npc_id)
                    if gs.player:
                        gs.add_log(t("app.log.social"))
                        gs.add_log(f"【初见形象】{gear_public_impression(gs.player)}")
                        gs.add_log(t("app.log.identity", gender=gs.player.gender))
                    opening = dialogue_engine.start_dialogue(gs, npc_id)
                    st.session_state.dialogue_session.add_turn("assistant", opening)
                    gs.add_log(f"{npc_id}：{opening[:80]}…")
                    st.session_state.ui_mode = "dialogue"
                elif ch.choice_id in ("dyn_spawn", "companion_seek", "companion_probe"):
                    pass
                else:
                    st.session_state.scene_text = engine.generate_scene_description(gs)
                st.rerun()


if __name__ == "__main__":
    main()
