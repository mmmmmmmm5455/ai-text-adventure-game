"""
角色创建预览面板
实时显示角色配置的预览
"""

import streamlit as st
from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CharacterPreviewState:
    """角色预览状态"""
    name: str = ""
    gender: str = ""
    profession: str = ""
    strength: int = 5
    intelligence: int = 5
    agility: int = 5
    charisma: int = 5
    perception: int = 5
    endurance: int = 5
    background_id: str | None = None
    background_name: str | None = None
    positive_traits: list[str] = field(default_factory=list)
    negative_traits: list[str] = field(default_factory=list)


def render_character_preview_sidebar(state: CharacterPreviewState, show_all: bool = True) -> None:
    """渲染角色预览侧边栏。

    Args:
        state: 角色预览状态
        show_all: 是否显示所有信息
    """
    st.markdown("## 👁️ 角色预览")
    st.markdown("---")

    # 基本信息
    st.markdown("### 📋 基本信息")
    st.info(f"**姓名：** {state.name or '未填写'}")
    st.info(f"**性别：** {state.gender}")
    st.info(f"**职业：** {state.profession}")

    # 属性信息
    st.markdown("### ⚔️ 属性")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("力量", state.strength)
        st.metric("智力", state.intelligence)
    with col2:
        st.metric("敏捷", state.agility)
        st.metric("魅力", state.charisma)
    with col3:
        st.metric("感知", state.perception)
        st.metric("耐力", state.endurance)

    # 属性总和
    total_points = (
        state.strength + state.intelligence + state.agility +
        state.charisma + state.perception + state.endurance
    )
    st.caption(f"**属性总和：** {total_points} / 20")

    if total_points == 20:
        st.success("✅ 属性分配正确")
    elif total_points > 20:
        st.error(f"❌ 超出 {total_points - 20} 点")
    else:
        st.warning(f"⚠️ 还剩 {20 - total_points} 点")

    # 背景和特质
    st.markdown("---")
    st.markdown("### 🎨 背景和特质")

    if state.background_name:
        st.info(f"**背景：** {state.background_name}")
    else:
        st.caption("背景：未选择")

    if state.positive_traits:
        st.success(f"**正面特质：** {', '.join(state.positive_traits) or '无'}")
    else:
        st.caption("正面特质：无")

    if state.negative_traits:
        st.warning(f"**负面特质：** {', '.join(state.negative_traits) or '无'}")
    else:
        st.caption("负面特质：无")

    # 详细信息（可选）
    if show_all:
        st.markdown("---")
        st.markdown("### 📊 详细信息")

        # 职业加成说明
        profession_bonuses = {
            "战士": "⚔️ 高 HP 和力量，适合近战",
            "法师": "🔮 高 MP 和智力，适合法术",
            "盗贼": "🗡️ 高敏捷，适合潜行",
            "吟游诗人": "🎵 高魅力，适合辅助"
        }
        st.caption(f"**职业特点：** {profession_bonuses.get(state.profession, '未知')}")

        # 属性建议
        if state.profession == "战士":
            st.caption("建议：力量和耐力优先")
        elif state.profession == "法师":
            st.caption("建议：智力和感知优先")
        elif state.profession == "盗贼":
            st.caption("建议：敏捷和感知优先")
        elif state.profession == "吟游诗人":
            st.caption("建议：魅力和智力优先")


def render_preview_comparison(
    state1: CharacterPreviewState,
    state2: CharacterPreviewState | None = None,
    label1: str = "配置 A",
    label2: str = "配置 B"
) -> None:
    """渲染角色配置对比。

    Args:
        state1: 配置 A
        state2: 配置 B（可选）
        label1: 配置 A 的标签
        label2: 配置 B 的标签
    """
    if state2 is None:
        return

    st.markdown("## 📊 角色配置对比")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {label1}")
        render_character_preview_sidebar(state1, show_all=False)

    with col2:
        st.markdown(f"### {label2}")
        render_character_preview_sidebar(state2, show_all=False)

    st.markdown("---")
    st.markdown("### ⚖️ 属性对比")

    # 属性对比
    attributes = ["strength", "intelligence", "agility", "charisma", "perception", "endurance"]
    attr_names = ["力量", "智力", "敏捷", "魅力", "感知", "耐力"]

    for attr, attr_name in zip(attributes, attr_names):
        val1 = getattr(state1, attr)
        val2 = getattr(state2, attr)

        if val1 > val2:
            st.success(f"**{attr_name}：** {val1} vs {val2} ({label1} 更强)")
        elif val2 > val1:
            st.error(f"**{attr_name}：** {val1} vs {val2} ({label2} 更强)")
        else:
            st.caption(f"**{attr_name}：** {val1} vs {val2} (平手)")

    st.markdown("---")
    st.markdown("### 📋 对比总结")

    # 比较 HP 和 MP
    profession_to_base = {
        "战士": (120, 30),
        "法师": (70, 80),
        "盗贼": (85, 45),
        "吟游诗人": (90, 55),
    }

    base_hp, base_mp = profession_to_base.get(state1.profession, (100, 50))
    hp1 = base_hp + (state1.endurance - 5) * 10
    mp1 = base_mp + (state1.intelligence - 6) * 5

    base_hp2, base_mp2 = profession_to_base.get(state2.profession, (100, 50))
    hp2 = base_hp2 + (state2.endurance - 5) * 10
    mp2 = base_mp2 + (state2.intelligence - 6) * 5

    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"**{label1} HP：** {hp1}")
        st.caption(f"**{label1} MP：** {mp1}")

    with col2:
        st.caption(f"**{label2} HP：** {hp2}")
        st.caption(f"**{label2} MP：** {mp2}")

    if hp1 > hp2:
        st.success(f"**{label1}** HP 更高（+{hp1 - hp2}）")
    elif hp2 > hp1:
        st.error(f"**{label2}** HP 更高（+{hp2 - hp1}）")
    else:
        st.caption("HP 相同")

    if mp1 > mp2:
        st.success(f"**{label1}** MP 更高（+{mp1 - mp2}）")
    elif mp2 > mp1:
        st.error(f"**{label2}** MP 更高（+{mp2 - mp1}）")
    else:
        st.caption("MP 相同")


def save_preset(state: CharacterPreviewState, preset_name: str) -> None:
    """保存角色预设。

    Args:
        state: 角色预览状态
        preset_name: 预设名称
    """
    if "character_presets" not in st.session_state:
        st.session_state.character_presets = {}

    st.session_state.character_presets[preset_name] = {
        "name": state.name,
        "gender": state.gender,
        "profession": state.profession,
        "strength": state.strength,
        "intelligence": state.intelligence,
        "agility": state.agility,
        "charisma": state.charisma,
        "perception": state.perception,
        "endurance": state.endurance,
        "background_id": state.background_id,
        "background_name": state.background_name,
        "positive_traits": list(state.positive_traits),
        "negative_traits": list(state.negative_traits),
    }

    st.success(f"✅ 预设 '{preset_name}' 已保存")


def load_preset(preset_name: str) -> CharacterPreviewState:
    """加载角色预设。

    Args:
        preset_name: 预设名称

    Returns:
        CharacterPreviewState 对象，如果不存在则返回 None
    """
    if "character_presets" not in st.session_state:
        return None

    preset_data = st.session_state.character_presets.get(preset_name)
    if not preset_data:
        return None

    return CharacterPreviewState(**preset_data)


def list_presets() -> list[str]:
    """列出所有保存的预设名称。

    Returns:
        预设名称列表
    """
    if "character_presets" in st.session_state:
        return list(st.session_state.character_presets.keys())
    else:
        return []


def delete_preset(preset_name: str) -> None:
    """删除角色预设。

    Args:
        preset_name: 预设名称
    """
    if "character_presets" not in st.session_state:
        return None

    if preset_name in st.session_state.character_presets:
        del st.session_state.character_presets[preset_name]
        st.success(f"✅ 预设 '{preset_name}' 已删除")


def render_preset_manager() -> None:
    """渲染预设管理器"""
    st.markdown("### 💾 配置管理")

    presets = list_presets()

    if presets:
        st.write("**已保存的配置：**")
        for preset in presets:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"📂 加载", key=f"load_{preset}"):
                    loaded = load_preset(preset)
                    if loaded:
                        # 更新 UI 状态
                        st.session_state.char_name = loaded.name
                        st.session_state.char_gender = loaded.gender
                        st.session_state.char_profession = loaded.profession
                        st.session_state.char_strength = loaded.strength
                        st.session_state.char_intelligence = loaded.intelligence
                        st.session_state.char_agility = loaded.agility
                        st.session_state.char_charisma = loaded.charisma
                        st.session_state.char_perception = loaded.perception
                        st.session_state.char_endurance = loaded.endurance
                        st.session_state.char_background_id = loaded.background_id
                        st.session_state.char_positive_traits = list(loaded.positive_traits)
                        st.session_state.char_negative_traits = list(loaded.negative_traits)
                        st.success(f"✅ 已加载预设：{preset}")
                        st.rerun()
            with col2:
                if st.button(f"💾 保存", key=f"save_{preset}"):
                    save_preset(
                        CharacterPreviewState(
                            name=st.session_state.char_name or "",
                            gender=st.session_state.char_gender or "",
                            profession=st.session_state.char_profession or "",
                            strength=st.session_state.char_strength,
                            intelligence=st.session_state.char_intelligence,
                            agility=st.session_state.char_agility,
                            charisma=st.session_state.char_charisma,
                            perception=st.session_state.char_perception,
                            endurance=st.session_state.char_endurance,
                            background_id=st.session_state.char_background_id,
                            background_name=st.session_state.char_background_name,
                            positive_traits=list(st.session_state.get("char_positive_traits", [])),
                            negative_traits=list(st.session_state.get("char_negative_traits", [])),
                        ),
                        preset
                    )
            with col3:
                if st.button(f"🗑️ 删除", key=f"delete_{preset}"):
                    delete_preset(preset)
                    st.rerun()
    else:
        st.caption("还没有保存的配置")
