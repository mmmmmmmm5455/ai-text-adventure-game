"""存档页：保存与读取（支持标签和描述）"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from core.config import get_settings
from core.exceptions import SaveLoadError
from core.i18n import t
from database.possession_db import possession_backend_ready
from game.game_state import GameState
from game.possession_bridge import resolve_possession_player_id, upload_snapshot_from_game_state
from game.save_metadata import (
    SaveMetadata,
    load_metadata,
    save_metadata,
    get_metadata_path,
    PREDEFINED_TAGS,
    get_suggested_tags,
)


def save_path() -> Path:
    return get_settings().saves_dir / "slot1.json"


def render_save_metadata_ui(save_path: Path, save_data: dict[str, Any] | None = None) -> SaveMetadata:
    """渲染存档元数据 UI（标签和描述）

    Args:
        save_path: 存档文件路径
        save_data: 存档数据（用于推荐标签）

    Returns:
        SaveMetadata 对象
    """
    st.markdown("### 🏷️ 存档元数据")

    # 加载现有元数据
    metadata = load_metadata(save_path)

    # 获取推荐标签
    suggested_tags = get_suggested_tags(save_data) if save_data else []

    # 描述输入
    description = st.text_area(
        "📝 存档描述",
        value=metadata.description,
        max_chars=200,
        help="为这个存档添加一个简短的描述（最多200字）",
        key="save_description"
    )

    # 标签选择
    st.markdown("#### 🏷️ 标签")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("**选择标签：**")
        selected_tags = []

        # 预定义标签
        for tag in PREDEFINED_TAGS:
            is_checked = tag in metadata.tags
            is_suggested = tag in suggested_tags

            # 显示标签
            label_text = f"{'🌟 ' if is_suggested else ''}{tag}"
            if st.checkbox(label_text, value=is_checked, key=f"tag_{tag}"):
                if tag not in selected_tags:
                    selected_tags.append(tag)

        # 自定义标签输入
        custom_tag = st.text_input(
            "➕ 添加自定义标签",
            max_chars=20,
            help="输入自定义标签后按回车",
            key="custom_tag_input"
        )

        if custom_tag and custom_tag not in metadata.tags:
            selected_tags.append(custom_tag)

    with col2:
        st.write("**已选择的标签：**")
        if selected_tags:
            for tag in selected_tags:
                st.info(f"• {tag}")
        else:
            st.caption("未选择标签")

        st.write("**推荐标签：**")
        if suggested_tags:
            for tag in suggested_tags:
                st.caption(f"🌟 {tag}")
        else:
            st.caption("暂无推荐")

    # 保存按钮
    if st.button("💾 保存元数据", type="secondary", key="save_metadata_btn"):
        # 更新元数据
        metadata.set_description(description)
        metadata.tags = list(selected_tags)

        try:
            save_metadata(save_path, metadata)
            st.success("✅ 元数据保存成功！")
        except IOError as e:
            st.error(f"❌ 保存元数据失败：{e}")

    return metadata


def render_archive(state: GameState | None) -> GameState | None:
    """返回加载后的状态（若成功）。"""
    st.subheader(t("archive.title"))
    p = save_path()
    st.caption(t("archive.slot", path=p))

    # 存档信息展示
    col_save, col_meta = st.columns([1, 1])

    with col_save:
        st.markdown("#### 💾 存档操作")
        c1, c2 = st.columns(2)
        with c1:
            if st.button(t("archive.save"), key="archive_save_btn"):
                if not state or not state.player:
                    st.error(t("archive.no_state"))
                else:
                    try:
                        state.save(p)
                        st.success(t("archive.saved"))
                        st.rerun()
                    except SaveLoadError as e:
                        st.error(str(e))

        with c2:
            if st.button(t("archive.load"), key="archive_load_btn"):
                try:
                    if not p.exists():
                        st.warning(t("archive.no_file"))
                        return state
                    loaded = GameState.load(p)
                    st.success(t("archive.loaded"))
                    return loaded
                except SaveLoadError as e:
                    st.error(str(e))

    with col_meta:
        st.markdown("#### 🏷️ 元数据管理")

        # 显示当前存档的元数据
        if p.exists():
            metadata = load_metadata(p)

            st.write("**当前标签：**")
            if metadata.tags:
                tag_cols = st.columns(3)
                for i, tag in enumerate(metadata.tags):
                    with tag_cols[i % 3]:
                        st.info(f"🏷️ {tag}")
            else:
                st.caption("暂无标签")

            st.write("**当前描述：**")
            if metadata.description:
                st.caption(metadata.description)
            else:
                st.caption("暂无描述")

            st.caption(f"**创建时间：** {metadata.created_at}")
            st.caption(f"**更新时间：** {metadata.updated_at}")
        else:
            st.caption("存档不存在，请先保存")

        # 元数据编辑区域
        if p.exists():
            with st.expander("✏️ 编辑元数据", expanded=False):
                # 读取存档数据以推荐标签
                save_data = None
                try:
                    import json
                    with open(p, "r", encoding="utf-8") as f:
                        save_data = json.load(f)
                except Exception:
                    pass

                render_save_metadata_ui(p, save_data)

    st.markdown("---")

    # 奪舍上传
    if possession_backend_ready():
        with st.expander(t("archive.possession_expander"), expanded=False):
            st.caption(t("archive.possession_hint"))
            pid_raw = st.text_input(t("archive.possession_player_id"), key="possession_player_uuid")
            with_llm = st.checkbox(t("archive.possession_last_words_llm"), value=False)
            if st.button(t("archive.possession_upload"), key="possession_upload_btn"):
                if not state or not state.player:
                    st.error(t("archive.no_state"))
                else:
                    pid = resolve_possession_player_id(pid_raw or None)
                    if pid is None:
                        st.error(t("archive.possession_bad_uuid"))
                    else:
                        llm = None
                        if with_llm:
                            from engine.llm_client import LLMClient

                            llm = LLMClient()
                        sid = upload_snapshot_from_game_state(
                            pid,
                            state,
                            label=t("archive.possession_label_default"),
                            generate_last_words_llm=llm,
                        )
                        if sid is None:
                            st.error(t("archive.possession_failed"))
                        else:
                            st.success(t("archive.possession_uploaded", snapshot_id=str(sid)))

    return state
