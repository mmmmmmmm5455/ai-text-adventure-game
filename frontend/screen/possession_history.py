"""
奪舍历史记录 UI 组件
显示玩家的奪舍历史
"""

import streamlit as st
from typing import Any
from datetime import datetime


def render_possession_history(history: list[dict[str, Any]], show_all: bool = False) -> None:
    """渲染奪舍历史记录。

    Args:
        history: 奪舍历史列表
        show_all: 是否显示所有信息
    """
    if not history:
        st.warning("还没有奪舍历史记录")
        return

    # 标题
    st.markdown(f"## 📜 奪舍历史记录 ({len(history)} 条)")

    # 统计信息
    st.markdown("### 📊 统计信息")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总奪舍次数", len(history))
    with col2:
        st.metric("最近奪舍", f"{history[0]['possessed_at'].strftime('%Y-%m-%d %H:%M') if isinstance(history[0]['possessed_at'], datetime) else history[0]['possessed_at']}")
    with col3:
        st.metric("最早奪舍", f"{history[-1]['possessed_at'].strftime('%Y-%m-%d %H:%M') if isinstance(history[-1]['possessed_at'], datetime) else history[-1]['possessed_at']}")

    # 历史列表
    st.markdown("---")
    st.markdown("### 📜 奪舍列表")

    for i, record in enumerate(history, 1):
        with st.expander(f"{i}. {record['character_name']} (Lv.{record['character_level']}) - {record['possessed_at'].strftime('%Y-%m-%d %H:%M') if isinstance(record['possessed_at'], datetime) else record['possessed_at']}", expanded=False):
            # 基本信息
            st.markdown("#### 📋 基本信息")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"**角色名：** {record['character_name']}")
                st.caption(f"**等级：** {record['character_level']}")
            with col2:
                st.caption(f"**奪舍时间：** {record['possessed_at'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(record['possessed_at'], datetime) else record['possessed_at']}")
                st.caption(f"**快照 ID：** {record['host_snapshot_id']}")
            with col3:
                st.caption(f"**玩家 ID：** {record['possessor_player_id']}")
                st.caption(f"**主机 ID：** {record['host_player_id']}")

            # 详情信息
            if show_all:
                st.markdown("#### 📊 详细信息")
                
                # 快照时间
                snapshot_time = record.get('snapshot_time')
                if snapshot_time:
                    if isinstance(snapshot_time, str):
                        snapshot_time = datetime.fromisoformat(snapshot_time.replace('Z', '+00:00'))
                    st.caption(f"**快照时间：** {snapshot_time.strftime('%Y-%m-%d %H:%M')}")

                # 章节信息
                chapter = record.get('game_chapter', 1)
                st.caption(f"**章节：** 第 {chapter} 章")

                # 操作按钮
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👁️ 查看快照", key=f"view_snapshot_{record['host_snapshot_id']}", type="secondary"):
                        st.info(f"快照 ID：{record['host_snapshot_id']}")
                with col2:
                    if st.button("🗑️ 删除记录", key=f"delete_record_{record['host_snapshot_id']}", type="secondary"):
                        st.warning(f"删除奪舍记录功能开发中...")

        st.divider()


def render_possession_summary(history: list[dict[str, Any]], max_show: int = 5) -> None:
    """渲染奪舍历史摘要（简洁版）。

    Args:
        history: 奪舍历史列表
        max_show: 最多显示数量
    """
    if not history:
        st.caption("还没有奪舍历史记录")
        return

    st.caption(f"📜 奪舍历史（最近 {min(max_show, len(history))} 次）")

    display_history = history[:max_show]

    for i, record in enumerate(display_history, 1):
        # 时间
        possessed_at = record['possessed_at']
        if isinstance(possessed_at, datetime):
            time_str = possessed_at.strftime("%m-%d %H:%M")
        else:
            time_str = str(possessed_at)

        st.caption(f"{i}. {record['character_name']} (Lv.{record['character_level']}) - {time_str}")

    if len(history) > max_show:
        st.caption(f"... 还有 {len(history) - max_show} 条记录")


def render_possession_statistics(history: list[dict[str, Any]]) -> None:
    """渲染奪舍统计信息。

    Args:
        history: 奪舍历史列表
    """
    if not history:
        st.warning("没有奪舍历史记录")
        return

    st.markdown("## 📊 奪舍统计")

    # 基本信息
    st.markdown("### 📋 基本信息")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总奪舍次数", len(history))
    with col2:
        if history:
            latest = history[0]['possessed_at']
            if isinstance(latest, datetime):
                st.metric("最近奪舍", latest.strftime("%Y-%m-%d %H:%M"))
            else:
                st.metric("最近奪舍", str(latest))
        else:
            st.metric("最近奪舍", "无")
    with col3:
        if history:
            earliest = history[-1]['possessed_at']
            if isinstance(earliest, datetime):
                st.metric("最早奪舍", earliest.strftime("%Y-%m-%d %H:%M"))
            else:
                st.metric("最早奪舍", str(earliest))
        else:
            st.metric("最早奪舍", "无")
    with col4:
        st.metric("不同角色数", len(set(r['character_name'] for r in history)))

    # 角色分布
    st.markdown("---")
    st.markdown("### 🎭 角色分布")

    character_counts = {}
    for record in history:
        name = record['character_name']
        character_counts[name] = character_counts.get(name, 0) + 1

    if character_counts:
        # 排序
        sorted_counts = sorted(character_counts.items(), key=lambda x: x[1], reverse=True)

        for name, count in sorted_counts:
            percentage = (count / len(history)) * 100
            st.write(f"**{name}**: {count} 次 ({percentage:.1f}%)")
            st.progress(percentage / 100)
    else:
        st.caption("没有角色数据")

    # 等级分布
    st.markdown("---")
    st.markdown("### ⚔️ 等级分布")

    level_counts = {}
    for record in history:
        level = record['character_level']
        level_counts[level] = level_counts.get(level, 0) + 1

    if level_counts:
        # 排序
        sorted_levels = sorted(level_counts.items(), key=lambda x: x[0])

        for level, count in sorted_levels:
            percentage = (count / len(history)) * 100
            st.write(f"**Lv.{level}**: {count} 次 ({percentage:.1f}%)")
            st.progress(percentage / 100)
    else:
        st.caption("没有等级数据")

    # 时间分布
    st.markdown("---")
    st.markdown("### ⏱️ 时间分布")

    # 按月统计
    monthly_counts = {}
    for record in history:
        possessed_at = record['possessed_at']
        if isinstance(possessed_at, datetime):
            month_key = possessed_at.strftime("%Y-%m")
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1

    if monthly_counts:
        sorted_months = sorted(monthly_counts.items())
        for month, count in sorted_months:
            percentage = (count / len(history)) * 100
            st.write(f"**{month}**: {count} 次 ({percentage:.1f}%)")
            st.progress(percentage / 100)
    else:
        st.caption("没有时间数据")


def render_possession_timeline(history: list[dict[str, Any]]) -> None:
    """渲染奪舍时间线。

    Args:
        history: 奪舍历史列表
    """
    if not history:
        st.warning("没有奪舍历史记录")
        return

    st.markdown("## ⏱️ 奪舍时间线")

    # 时间线
    for i, record in enumerate(history):
        possessed_at = record['possessed_at']
        
        if isinstance(possessed_at, datetime):
            time_str = possessed_at.strftime("%Y-%m-%d %H:%M")
            date_str = possessed_at.strftime("%Y-%m-%d")
            is_today = possessed_at.date() == datetime.now().date()
            
            if is_today:
                time_str += " (今天)"
        else:
            time_str = str(possessed_at)
            date_str = time_str

        # 显示时间线节点
        st.markdown(f"**{date_str}** - {time_str}")
        st.success(f"🎭 奪舍了 **{record['character_name']}** (Lv.{record['character_level']})")
        
        st.caption(f"快照 ID: {record['host_snapshot_id']}")
        
        st.divider()


def render_possession_comparison(history: list[dict[str, Any]], compare_recent: int = 5) -> None:
    """对比最近的几次奪舍。

    Args:
        history: 奪舍历史列表
        compare_recent: 对比最近的几次奪舍
    """
    if not history:
        st.warning("没有奪舍历史记录")
        return

    st.markdown(f"## 📊 最近 {min(compare_recent, len(history))} 次奪舍对比")

    compare_history = history[:compare_recent]

    for i, record in enumerate(compare_history, 1):
        st.markdown(f"### {i}. {record['character_name']} (Lv.{record['character_level']})")

        col1, col2 = st.columns(2)
        
        with col1:
            st.caption(f"**奪舍时间：** {record['possessed_at'].strftime('%Y-%m-%d %H:%M') if isinstance(record['possessed_at'], datetime) else record['possessed_at']}")
            st.caption(f"**快照 ID：** {record['host_snapshot_id']}")
        
        with col2:
            # 快照时间
            snapshot_time = record.get('snapshot_time')
            if snapshot_time:
                if isinstance(snapshot_time, str):
                    snapshot_time = datetime.fromisoformat(snapshot_time.replace('Z', '+00:00'))
                st.caption(f"**快照时间：** {snapshot_time.strftime('%Y-%m-%d %H:%M')}")
            
            # 章节
            chapter = record.get('game_chapter', 1)
            st.caption(f"**章节：** 第 {chapter} 章")

        st.divider()
