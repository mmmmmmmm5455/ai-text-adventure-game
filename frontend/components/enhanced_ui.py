"""
增强的 UI 组件 - 使用新主题
"""

from __future__ import annotations

import streamlit as st
from typing import Any

from core.i18n import t
from game.companion import get_active_companion
from game.game_state import GameState


def render_player_status_enhanced(state: GameState, theme: str = "retro-futuristic") -> None:
    """渲染增强的玩家状态面板

    Args:
        state: 游戏状态
        theme: 主题名称
    """
    p = state.player
    if not p:
        st.info(t("status.no_player"))
        return

    # 角色信息卡片
    with st.container():
        st.markdown("### 👤 角色状态")
        st.markdown(f"**{p.name}** · {p.profession.value} · {p.gender} · Lv.{p.level}")

        # HP 和 MP 进度条（带颜色）
        hp_percent = min(100, int(p.hp / max(1, p.max_hp) * 100))
        mp_percent = min(100, int(p.mp / max(1, p.max_mp) * 100))

        # HP 颜色（根据 HP 百分比）
        hp_color = "#00ff41" if hp_percent > 50 else "#ff6b35" if hp_percent > 25 else "#ff0000"

        st.markdown(
            f"""
<div style="margin: 0.5rem 0;">
  <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
    <span>❤️ HP</span>
    <span>{p.hp}/{p.max_hp}</span>
  </div>
  <div style="background: rgba(0,0,0,0.3); border-radius: 4px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">
    <div style="width: {hp_percent}%; background: {hp_color}; height: 8px; animation: pulse 2s ease-in-out infinite;"></div>
  </div>
</div>
<div style="margin: 0.5rem 0;">
  <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
    <span>🔮 MP</span>
    <span>{p.mp}/{p.max_mp}</span>
  </div>
  <div style="background: rgba(0,0,0,0.3); border-radius: 4px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">
    <div style="width: {mp_percent}%; background: #00ffff; height: 8px; animation: pulse 2s ease-in-out infinite;"></div>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )

        # 金币和经验
        st.caption(f"💰 金币: {p.gold} | ✨ 经验: {p.xp}")

        st.divider()

    # 属性显示
    with st.container():
        st.markdown("### 📊 属性")

        stats = {
            "⚔️ 力量": p.strength,
            "🔮 智力": p.intelligence,
            "🗡️ 敏捷": p.agility,
            "🎭 魅力": p.charisma,
            "👁️ 感知": p.perception,
            "🛡️ 耐力": p.endurance,
        }

        for name, value in stats.items():
            st.markdown(
                f"""
<div class="stat-display">
  <span class="stat-name">{name}</span>
  <span class="stat-value">{value}</span>
</div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

    # 伙伴信息
    comp = get_active_companion(state)
    if comp:
        with st.container():
            st.markdown("### 🤝 伙伴")
            st.markdown(f"**{comp.get('name', '?')}**")
            st.caption(comp.get("special_skill", ""))

            loyalty = int(comp.get("loyalty_score", 50))
            st.caption(f"💖 忠诚度: {loyalty}%")

            st.markdown(
                f"""
<div style="background: rgba(0,0,0,0.3); border-radius: 4px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">
  <div style="width: {loyalty}%; background: #ff00ff; height: 6px;"></div>
</div>
                """,
                unsafe_allow_html=True,
            )

            st.divider()

    # 位置和时间
    with st.container():
        st.markdown("### 📍 位置信息")
        st.caption(f"🌍 场景: {state.current_scene_id}")
        st.caption(f"⏰ 时间: {state.time_label()}")
        st.caption(f"🔄 回合: {state.round_count}")
        st.divider()

    # 已完成任务
    with st.container():
        st.markdown("### ✅ 已完成任务")
        done = [q.name for q in state.quests.completed_quests()]
        if done:
            for n in done:
                st.markdown(
                    f"""
<div class="quest-item completed">
  <span>✓ {n}</span>
</div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("暂无已完成任务")


def render_scene_card_enhanced(title: str, body: str, theme: str = "retro-futuristic") -> None:
    """渲染增强的场景卡片

    Args:
        title: 场景标题
        body: 场景内容
        theme: 主题名称
    """
    st.markdown(
        f"""
<div class="scene-card">
  <h2 class="scene-title">{title}</h2>
  <div class="scene-body">{body}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_choice_list_enhanced(choices: list[str], theme: str = "retro-futuristic") -> int | None:
    """渲染增强的选择列表

    Args:
        choices: 选项列表
        theme: 主题名称

    Returns:
        选中的索引（从 0 开始），如果没有选择则返回 None
    """
    if not choices:
        return None

    st.markdown("### 🎯 选择行动")

    for i, choice in enumerate(choices):
        if st.button(f"{i + 1}. {choice}", key=f"choice_{i}"):
            return i

    return None


def render_chat_message_enhanced(
    role: str,
    content: str,
    theme: str = "retro-futuristic"
) -> None:
    """渲染增强的聊天消息

    Args:
        role: 角色 (user, assistant, system)
        content: 消息内容
        theme: 主题名称
    """
    role_map = {
        "user": "玩家",
        "assistant": "AI",
        "system": "系统",
    }

    role_label = role_map.get(role, role)
    role_class = role

    st.markdown(
        f"""
<div class="chat-message {role_class}">
  <div style="font-weight: 700; color: var(--accent-cyan); margin-bottom: 0.5rem;">
    {role_label}
  </div>
  <div class="message-content">{content}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_progress_bar_enhanced(
    value: float,
    max_value: float,
    label: str,
    color: str = "#00ff41",
    theme: str = "retro-futuristic"
) -> None:
    """渲染增强的进度条

    Args:
        value: 当前值
        max_value: 最大值
        label: 标签
        color: 颜色（十六进制）
        theme: 主题名称
    """
    percent = min(100, int(value / max(1, max_value) * 100))

    st.markdown(
        f"""
<div style="margin: 0.5rem 0;">
  <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
    <span>{label}</span>
    <span>{value}/{max_value} ({percent}%)</span>
  </div>
  <div style="background: rgba(0,0,0,0.3); border-radius: 4px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">
    <div style="width: {percent}%; background: {color}; height: 8px; animation: pulse 2s ease-in-out infinite;"></div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_typing_effect(text: str, delay: float = 0.05) -> None:
    """渲染打字机效果（简化版，Streamlit 不支持真正的打字机动画）

    Args:
        text: 要显示的文本
        delay: 延迟时间（秒）
    """
    # Streamlit 不支持动态动画，所以这里只是添加光标效果
    st.markdown(
        f"""
<div style="display: inline-block;">
  {text}<span class="cursor-blink"></span>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_notification(
    message: str,
    type: str = "info",
    theme: str = "retro-futuristic"
) -> None:
    """渲染通知消息

    Args:
        message: 消息内容
        type: 类型 (info, success, warning, error)
        theme: 主题名称
    """
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
    }

    colors = {
        "info": "#00ffff",
        "success": "#00ff41",
        "warning": "#ff6b35",
        "error": "#ff0000",
    }

    icon = icons.get(type, "ℹ️")
    color = colors.get(type, "#00ffff")

    st.markdown(
        f"""
<div style="
  background: rgba(0,0,0,0.5);
  border-left: 3px solid {color};
  border-radius: 8px;
  padding: 1rem;
  margin: 0.5rem 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
">
  <div style="display: flex; align-items: center; gap: 0.5rem;">
    <span style="font-size: 1.5rem;">{icon}</span>
    <span style="flex: 1;">{message}</span>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
