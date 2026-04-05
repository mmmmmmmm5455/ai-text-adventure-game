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

import streamlit as st

from core.logger import setup_logging
from engine.ai_dialogue import DialogueSession
from engine.event_handler import maybe_trigger_event
from engine.story_engine import StoryEngine, grant_starting_items
from frontend.components.chat import render_chat_history
from frontend.components.player_status import render_player_status
from frontend.components.quest_list import render_quest_list
from frontend.components.scene_card import render_scene_card
from frontend.pages.archive import render_archive, save_path
from frontend.pages.home import render_home
from frontend.pages.settings import render_settings
from story.world_config import WORLD_LORE, WORLD_NAME, new_game_state
from utils.helpers import validate_user_text


@st.cache_resource
def get_engine() -> StoryEngine:
    return StoryEngine()


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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def main() -> None:
    setup_logging()
    _inject_css()
    _init_session()
    st.set_page_config(page_title=f"{WORLD_NAME} · AI 文字冒险", layout="wide")
    engine = get_engine()

    with st.sidebar:
        st.title(WORLD_NAME)
        st.caption("AI 文字冒险游戏引擎")
        if st.button("新游戏"):
            st.session_state.game_state = None
            st.session_state.ui_mode = "home"
            st.session_state.scene_text = ""
            st.session_state.dialogue_session = None
            st.session_state.pending_dialogue_npc = None
            st.session_state.pop("ending_text", None)
            st.rerun()

        st.divider()
        st.session_state.game_state = render_archive(st.session_state.game_state)

        if st.button("设置与模型信息"):
            st.session_state.ui_mode = "settings"
            st.rerun()

        st.divider()
        st.caption("帮助：先创建角色，在探索中点击与 NPC 交谈进入对话；可随时保存。")

    gs = st.session_state.game_state

    left, mid, right = st.columns([1.1, 2.2, 1.1])

    with left:
        if gs:
            render_player_status(gs)

    with right:
        if gs:
            st.subheader("冒险日志")
            for line in gs.game_log[-12:]:
                st.caption(line)
            st.divider()
            st.subheader("背包")
            if gs.player:
                for it in gs.player.inventory.items:
                    st.write(f"- {it.name} x{it.quantity}")
            st.divider()
            render_quest_list(gs)

    with mid:
        if st.session_state.ui_mode == "settings":
            render_settings()
            if st.button("返回"):
                st.session_state.ui_mode = "explore" if gs else "home"
                st.rerun()
            return

        if st.session_state.ui_mode == "home" or gs is None:
            st.markdown(f"### {WORLD_NAME}")
            st.write(WORLD_LORE)
            name, prof = render_home()
            if name and prof:
                with st.spinner("正在初始化世界与生成开场氛围…"):
                    ngs = new_game_state(name, prof)
                    grant_starting_items(ngs)
                    try:
                        ok = engine.llm.health_check()
                        st.session_state.ollama_ok = ok
                    except Exception:
                        st.session_state.ollama_ok = False
                    txt = engine.generate_scene_description(ngs)
                    ngs.add_log("冒险开始。")
                    st.session_state.game_state = ngs
                    st.session_state.scene_text = txt
                    st.session_state.ui_mode = "explore"
                    st.rerun()
            return

        assert gs is not None

        if st.session_state.ui_mode == "dialogue" and st.session_state.dialogue_session:
            sess: DialogueSession = st.session_state.dialogue_session
            st.subheader("对话")
            msgs = [(r, c) for r, c in sess.history]
            render_chat_history(msgs)
            user_in = st.chat_input("输入你想说的话…")
            if user_in:
                ok, err = validate_user_text(user_in)
                if not ok:
                    st.error(err)
                else:
                    with st.spinner("NPC 思考中…"):
                        reply, _clues = engine.continue_dialogue(gs, sess, user_in)
                        gs.add_log(f"对话：{reply[:80]}…" if len(reply) > 80 else f"对话：{reply}")
                    st.rerun()
            c1, c2 = st.columns(2)
            with c1:
                if st.button("结束对话"):
                    closing = engine.end_dialogue(gs, sess)
                    gs.add_log(closing)
                    st.session_state.dialogue_session = None
                    st.session_state.ui_mode = "explore"
                    st.rerun()
            with c2:
                if st.button("刷新场景描写"):
                    with st.spinner("生成场景…"):
                        st.session_state.scene_text = engine.generate_scene_description(gs)
                    st.rerun()
            return

        st.subheader("探索")
        if st.session_state.ollama_ok is False:
            st.info("未检测到可用的 Ollama 服务，将使用离线降级文本；安装并启动 Ollama 可获得更佳体验。")

        render_scene_card("当前场景", st.session_state.scene_text or "（点击刷新场景描写）")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("刷新场景描写"):
                with st.spinner("正在生成…"):
                    st.session_state.scene_text = engine.generate_scene_description(gs)
                st.rerun()
        with c2:
            if st.button("随机事件（概率触发）"):
                ev = maybe_trigger_event(gs)
                if ev:
                    gs.add_log(ev.message)
                st.rerun()
        with c3:
            if st.button("生成结局长文（调用模型）"):
                with st.spinner("书写结局…"):
                    st.session_state["ending_text"] = engine.generate_ending_narrative(gs)
                st.rerun()

        if "ending_text" in st.session_state and st.session_state["ending_text"]:
            st.success(st.session_state["ending_text"])

        st.divider()
        st.caption("选择一项行动：")
        choices = engine.generate_choices(gs)
        for ch in choices:
            if st.button(ch.label, key=f"ch_{ch.choice_id}"):
                with st.spinner("处理中…"):
                    msg, enter_talk = engine.process_choice(gs, ch.choice_id)
                gs.add_log(msg[:120])
                if enter_talk and ch.choice_id.startswith("talk:"):
                    npc_id = ch.choice_id.split(":", 1)[1]
                    st.session_state.dialogue_session = DialogueSession(npc_id=npc_id)
                    opening = engine.start_dialogue(gs, npc_id)
                    st.session_state.dialogue_session.add_turn("assistant", opening)
                    gs.add_log(f"{npc_id}：{opening[:80]}…")
                    st.session_state.ui_mode = "dialogue"
                else:
                    st.session_state.scene_text = engine.generate_scene_description(gs)
                st.rerun()


if __name__ == "__main__":
    main()
