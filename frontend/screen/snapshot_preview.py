"""
快照预览 UI 组件
显示奪舍快照的详细信息
"""

import streamlit as st
from typing import Any
from datetime import datetime


def render_snapshot_preview(snapshot: dict[str, Any], show_all: bool = False) -> None:
    """渲染快照预览卡片。

    Args:
        snapshot: 快照数据字典
        show_all: 是否显示所有信息
    """
    # 标题
    st.markdown(f"## 👁️ {snapshot['character_name']} 的快照")

    # 基本信息
    st.markdown("### 📋 基本信息")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("角色名", snapshot['character_name'])
    with col2:
        st.metric("等级", snapshot['character_level'])
    with col3:
        st.metric("背景", snapshot['character_bg_name'] or "无")
    with col4:
        st.metric("章节", snapshot.get('game_chapter', 1))

    # 状态信息
    st.markdown("---")
    st.markdown("### 💚 状态")

    # HP
    if snapshot['character_hp'] is not None and snapshot['character_max_hp'] is not None:
        hp_percent = round(snapshot['character_hp'] / snapshot['character_max_hp'] * 100, 1) if snapshot['character_max_hp'] > 0 else 0
        st.metric(
            "HP",
            f"{snapshot['character_hp']}/{snapshot['character_max_hp']}",
            delta=f"{hp_percent}%",
            delta_color="normal" if hp_percent > 50 else "inverse"
        )
        st.progress(hp_percent / 100)
    else:
        st.caption("HP 数据不可用")

    # 时间信息
    st.markdown("---")
    st.markdown("### ⏱️ 时间信息")

    snapshot_time = snapshot['snapshot_time']
    if isinstance(snapshot_time, str):
        snapshot_time = datetime.fromisoformat(snapshot_time.replace('Z', '+00:00'))
    
    playtime = snapshot.get('playtime_minutes', 0)
    if playtime > 0:
        hours = playtime // 60
        minutes = playtime % 60
        if hours > 0:
            playtime_str = f"{hours}小时{minutes}分钟"
        else:
            playtime_str = f"{minutes}分钟"
    else:
        playtime_str = "未知"

    col1, col2 = st.columns(2)
    with col1:
        st.metric("快照时间", snapshot_time.strftime("%Y-%m-%d %H:%M"))
    with col2:
        st.metric("游戏时长", playtime_str)

    # 标签
    if snapshot['snapshot_label']:
        st.markdown("---")
        st.markdown("### 🏷️ 标签")
        st.success(f"**标签：** {snapshot['snapshot_label']}")

    # 最后遗言
    if snapshot['last_words']:
        st.markdown("---")
        st.markdown("### 💬 最后遗言")
        st.info(f"\"{snapshot['last_words']}\"")

    # 最近事件
    if show_all and snapshot['recent_events']:
        st.markdown("---")
        st.markdown("### 📜 最近事件")

        for i, event in enumerate(snapshot['recent_events'][:5], 1):
            event_type = event.get('event_type', '未知')
            event_summary = event.get('event_summary', '无描述')
            round_count = event.get('round_count', 'N/A')

            st.caption(f"**事件 {i}** (第 {round_count} 回合)")
            st.caption(f"类型：{event_type}")
            st.success(event_summary)
            st.divider()

        if len(snapshot['recent_events']) > 5:
            st.caption(f"... 还有 {len(snapshot['recent_events']) - 5} 个事件")

    # 主机信息
    st.markdown("---")
    st.markdown("### 👤 主机信息")
    st.caption(f"创建者：{snapshot['host_display_name']}")

    # 操作按钮
    if show_all:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🎭 奪舍这个角色", key=f"claim_{snapshot['snapshot_id']}", type="primary"):
                st.session_state.selected_snapshot_id = snapshot['snapshot_id']
                st.success(f"已选择：{snapshot['character_name']}")

        with col2:
            if st.button("📊 查看详细统计", key=f"stats_{snapshot['snapshot_id']}"):
                st.info("详细统计功能开发中...")

        with col3:
            if st.button("❌ 取消", key=f"cancel_{snapshot['snapshot_id']}"):
                st.session_state.selected_snapshot_id = None
                st.rerun()


def render_snapshot_summary(snapshot: dict[str, Any]) -> None:
    """渲染快照摘要（简洁版）。

    Args:
        snapshot: 快照数据字典
    """
    # 基本信息
    hp_status = ""
    if snapshot['character_hp'] is not None and snapshot['character_max_hp'] is not None:
        hp_percent = round(snapshot['character_hp'] / snapshot['character_max_hp'] * 100, 1) if snapshot['character_max_hp'] > 0 else 0
        hp_status = f"HP: {snapshot['character_hp']}/{snapshot['character_max_hp']} ({hp_percent}%)"

    with st.expander(f"👁️ {snapshot['character_name']} - Lv.{snapshot['character_level']} {snapshot['character_bg_name'] or ''}", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.caption(f"**章节：** {snapshot.get('game_chapter', 1)}")
            st.caption(f"**标签：** {snapshot['snapshot_label'] or '无'}")

        with col2:
            st.caption(f"**{hp_status}**")
            
            playtime = snapshot.get('playtime_minutes', 0)
            if playtime > 0:
                hours = playtime // 60
                minutes = playtime % 60
                if hours > 0:
                    playtime_str = f"{hours}h {minutes}m"
                else:
                    playtime_str = f"{minutes}m"
            else:
                playtime_str = "未知"
            st.caption(f"**时长：** {playtime_str}")

        with col3:
            if snapshot['last_words']:
                st.caption(f"**遗言：** \"{snapshot['last_words'][:30]}...\"")
            else:
                st.caption("**遗言：** 无")

        st.caption(f"**创建者：** {snapshot['host_display_name']}")

        # 操作按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🎭 奪舍", key=f"claim_summary_{snapshot['snapshot_id']}", type="secondary"):
                st.session_state.selected_snapshot_id = snapshot['snapshot_id']
                st.success(f"已选择：{snapshot['character_name']}")
        
        with col2:
            if st.button(f"👁️ 详情", key=f"detail_summary_{snapshot['snapshot_id']}", type="secondary"):
                st.session_state.selected_snapshot_id = snapshot['snapshot_id']
                st.session_state.show_detail = True
                st.rerun()


def render_snapshot_comparison(snapshot1: dict[str, Any], snapshot2: dict[str, Any]) -> None:
    """渲染两个快照的对比。

    Args:
        snapshot1: 第一个快照
        snapshot2: 第二个快照
    """
    st.markdown("## 📊 快照对比")

    # 基本信息
    st.markdown("### 📋 基本信息")
    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**快照 A：** {snapshot1['character_name']}")
        st.caption(f"等级：{snapshot1['character_level']}")
        st.caption(f"背景：{snapshot1['character_bg_name'] or '无'}")
        st.caption(f"章节：{snapshot1.get('game_chapter', 1)}")
        st.caption(f"标签：{snapshot1['snapshot_label'] or '无'}")

    with col2:
        st.info(f"**快照 B：** {snapshot2['character_name']}")
        st.caption(f"等级：{snapshot2['character_level']}")
        st.caption(f"背景：{snapshot2['character_bg_name'] or '无'}")
        st.caption(f"章节：{snapshot2.get('game_chapter', 1)}")
        st.caption(f"标签：{snapshot2['snapshot_label'] or '无'}")

    # HP 对比
    st.markdown("---")
    st.markdown("### 💚 HP 对比")

    col1, col2 = st.columns(2)

    with col1:
        if snapshot1['character_hp'] is not None and snapshot1['character_max_hp'] is not None:
            hp1_percent = round(snapshot1['character_hp'] / snapshot1['character_max_hp'] * 100, 1) if snapshot1['character_max_hp'] > 0 else 0
            st.info(f"**快照 A HP：** {snapshot1['character_hp']}/{snapshot1['character_max_hp']} ({hp1_percent}%)")
        else:
            st.info("**快照 A HP：** 不可用")

    with col2:
        if snapshot2['character_hp'] is not None and snapshot2['character_max_hp'] is not None:
            hp2_percent = round(snapshot2['character_hp'] / snapshot2['character_max_hp'] * 100, 1) if snapshot2['character_max_hp'] > 0 else 0
            st.info(f"**快照 B HP：** {snapshot2['character_hp']}/{snapshot2['character_max_hp']} ({hp2_percent}%)")
        else:
            st.info("**快照 B HP：** 不可用")

    # 遗言对比
    if snapshot1['last_words'] or snapshot2['last_words']:
        st.markdown("---")
        st.markdown("### 💬 最后遗言")

        col1, col2 = st.columns(2)

        with col1:
            if snapshot1['last_words']:
                st.info(f"**快照 A：** \"{snapshot1['last_words']}\"")
            else:
                st.info("**快照 A：** 无")

        with col2:
            if snapshot2['last_words']:
                st.info(f"**快照 B：** \"{snapshot2['last_words']}\"")
            else:
                st.info("**快照 B：** 无")


def render_snapshot_list(snapshots: list[dict[str, Any]], max_show: int = 10) -> None:
    """渲染快照列表。

    Args:
        snapshots: 快照列表
        max_show: 最多显示数量
    """
    if not snapshots:
        st.warning("没有可奪舍的快照")
        return

    st.markdown(f"## 👁️ 可奪舍快照 ({len(snapshots)} 个)")

    # 搜索框
    search = st.text_input("🔍 搜索角色名", key="snapshot_search")

    if search:
        snapshots = [s for s in snapshots if search.lower() in s['character_name'].lower()]
        st.caption(f"搜索结果：{len(snapshots)} 个")

    # 显示前 max_show 个
    display_snapshots = snapshots[:max_show]

    for i, snapshot in enumerate(display_snapshots, 1):
        st.markdown(f"**{i}. {snapshot['character_name']}** - Lv.{snapshot['character_level']} {snapshot['character_bg_name'] or ''}")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # HP
            if snapshot['character_hp'] is not None and snapshot['character_max_hp'] is not None:
                hp_percent = round(snapshot['character_hp'] / snapshot['character_max_hp'] * 100, 1) if snapshot['character_max_hp'] > 0 else 0
                st.caption(f"HP: {hp_percent}%")
            else:
                st.caption("HP: N/A")

        with col2:
            # 标签
            st.caption(f"标签: {snapshot['snapshot_label'] or '无'}")

        with col3:
            # 遗言
            if snapshot['last_words']:
                st.caption(f"遗言: \"{snapshot['last_words'][:20]}...\"")
            else:
                st.caption("遗言: 无")

        with col4:
            # 操作
            if st.button(f"👁️ 详情", key=f"list_detail_{snapshot['snapshot_id']}", type="secondary"):
                st.session_state.selected_snapshot = snapshot
                st.rerun()
            if st.button(f"🎭 奪舍", key=f"list_claim_{snapshot['snapshot_id']}", type="primary"):
                st.session_state.selected_snapshot_id = snapshot['snapshot_id']
                st.success(f"已选择：{snapshot['character_name']}")

        st.divider()

    if len(snapshots) > max_show:
        st.caption(f"... 还有 {len(snapshots) - max_show} 个快照")
