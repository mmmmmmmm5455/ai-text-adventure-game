"""
角色创建界面：属性分配、背景选择、特质选择
包含实时预览功能
"""

from __future__ import annotations

import streamlit as st

from game.character_creator import (
    CharacterCreator,
    CharacterCreatorConfig,
)
from game.player import Player, Profession
from frontend.screen.character_preview import (
    CharacterPreviewState,
    render_character_preview_sidebar,
    render_preview_comparison,
    save_preset,
    load_preset,
    list_presets,
    delete_preset,
    render_preset_manager
)


def _get_profession_from_name(profession_name: str) -> Profession:
    """从职业名称获取 Profession 枚举值"""
    mapping = {
        "战士": Profession.WARRIOR,
        "法师": Profession.MAGE,
        "盗贼": Profession.ROGUE,
        "吟游诗人": Profession.BARD,
    }
    return mapping.get(profession_name, Profession.WARRIOR)


def render_character_creation_ui() -> Player | None:
    """渲染完整的角色创建界面，包含实时预览。

    Returns:
        Player 对象，如果用户取消则返回 None
    """
    st.title("🎭 创建你的角色")
    st.markdown("---")

    # 获取可用的特质列表
    config = CharacterCreatorConfig.load()
    positive_traits = [t.name for t in config.positive_traits]
    negative_traits = [t.name for t in config.negative_traits]

    # 初始化 session_state
    if "char_name" not in st.session_state:
        st.session_state.char_name = ""
    if "char_gender" not in st.session_state:
        st.session_state.char_gender = "男"
    if "char_profession" not in st.session_state:
        st.session_state.char_profession = "战士"
    if "char_strength" not in st.session_state:
        st.session_state.char_strength = 5
    if "char_intelligence" not in st.session_state:
        st.session_state.char_intelligence = 5
    if "char_agility" not in st.session_state:
        st.session_state.char_agility = 5
    if "char_charisma" not in st.session_state:
        st.session_state.char_charisma = 5
    if "char_perception" not in st.session_state:
        st.session_state.char_perception = 5
    if "char_endurance" not in st.session_state:
        st.session_state.char_endurance = 5
    if "char_background_id" not in st.session_state:
        st.session_state.char_background_id = None
    if "char_background_name" not in st.session_state:
        st.session_state.char_background_name = None
    if "char_positive_traits" not in st.session_state:
        st.session_state.char_positive_traits = []
    if "char_negative_traits" not in st.session_state:
        st.session_state.char_negative_traits = []
    if "char_preview_mode" not in st.session_state:
        st.session_state.char_preview_mode = "sidebar"  # sidebar 或 bottom

    # 创建主布局
    col_main, col_preview = st.columns([2, 1])

    with col_main:
        # 基本信息
        st.markdown("### 📋 基本信息")
        name = st.text_input(
            "角色名字",
            max_chars=32,
            value=st.session_state.char_name,
            key="char_name"
        )
        st.session_state.char_name = name

        gender = st.selectbox(
            "性别",
            ["男", "女"],
            index=["男", "女"].index(st.session_state.char_gender) if st.session_state.char_gender in ["男", "女"] else 0,
            key="char_gender"
        )
        st.session_state.char_gender = gender

        profession = st.selectbox(
            "职业",
            ["战士", "法师", "盗贼", "吟游诗人"],
            index=["战士", "法师", "盗贼", "吟游诗人"].index(st.session_state.char_profession) if st.session_state.char_profession in ["战士", "法师", "盗贼", "吟游诗人"] else 0,
            key="char_profession"
        )
        st.session_state.char_profession = profession

        st.markdown("---")

        # 属性分配
        st.markdown("### 📊 分配属性点（共 20 点）")

        # 属性滑块
        col1, col2 = st.columns(2)
        with col1:
            strength = st.slider(
                "力量", 1, 10,
                st.session_state.char_strength, key="strength"
            )
            intelligence = st.slider(
                "智力", 1, 10,
                st.session_state.char_intelligence, key="intelligence"
            )
            agility = st.slider(
                "敏捷", 1, 10,
                st.session_state.char_agility, key="agility"
            )

        with col2:
            charisma = st.slider(
                "魅力", 1, 10,
                st.session_state.char_charisma, key="charisma"
            )
            perception = st.slider(
                "感知", 1, 10,
                st.session_state.char_perception, key="perception"
            )
            endurance = st.slider(
                "耐力", 1, 10,
                st.session_state.char_endurance, key="endurance"
            )

        # 更新 session_state
        st.session_state.char_strength = strength
        st.session_state.char_intelligence = intelligence
        st.session_state.char_agility = agility
        st.session_state.char_charisma = charisma
        st.session_state.char_perception = perception
        st.session_state.char_endurance = endurance

        # 计算总点数
        total_points = strength + intelligence + agility + charisma + perception + endurance

        # 显示总点数
        if total_points == 20:
            st.success(f"✅ 已分配：{total_points} / 20 点")
        elif total_points > 20:
            st.error(f"❌ 已分配：{total_points} / 20 点（超出 {total_points - 20} 点）")
        else:
            st.info(f"⚠️ 已分配：{total_points} / 20 点（还剩 {20 - total_points} 点）")

        # 快捷分配按钮
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🎲 随机分配", key="random_alloc"):
                import random
                # 随机分配 20 点
                attrs = [1] * 6
                remaining = 20 - 6

                for _ in range(remaining):
                    idx = random.randint(0, 5)
                    if attrs[idx] < 10:
                        attrs[idx] += 1
                    else:
                        # 如果某个属性已满，找其他属性
                        for j in range(6):
                            if attrs[j] < 10:
                                attrs[j] += 1
                                break

                st.session_state.char_strength = attrs[0]
                st.session_state.char_intelligence = attrs[1]
                st.session_state.char_agility = attrs[2]
                st.session_state.char_charisma = attrs[3]
                st.session_state.char_perception = attrs[4]
                st.session_state.char_endurance = attrs[5]
                st.rerun()

        with col2:
            if st.button("⭐ 推荐分配", key="recommended_alloc"):
                # 根据职业推荐属性（修正为总和 20）
                profession_to_attrs = {
                    "战士": [8, 3, 2, 2, 3, 2],
                    "法师": [3, 8, 2, 3, 2, 2],
                    "盗贼": [2, 3, 8, 2, 3, 2],
                    "吟游诗人": [2, 3, 2, 8, 3, 2],
                }
                recommended = profession_to_attrs.get(profession, [5, 5, 5, 5, 5, 5])

                st.session_state.char_strength = recommended[0]
                st.session_state.char_intelligence = recommended[1]
                st.session_state.char_agility = recommended[2]
                st.session_state.char_charisma = recommended[3]
                st.session_state.char_perception = recommended[4]
                st.session_state.char_endurance = recommended[5]
                st.rerun()

        with col3:
            if st.button("🔄 重置", key="reset_alloc"):
                st.session_state.char_strength = 5
                st.session_state.char_intelligence = 5
                st.session_state.char_agility = 5
                st.session_state.char_charisma = 5
                st.session_state.char_perception = 5
                st.session_state.char_endurance = 5
                st.rerun()

        st.markdown("---")

        # 背景选择
        st.markdown("### 📜 选择背景")

        backgrounds = {
            "wasteland_doctor": {
                "name": "廢土醫生",
                "description": "在廢墟間救治傷患，救死扶傷是你的天職。",
                "recommended_traits": ["first_aid_master", "calm_minded"]
            },
            "scavenger": {
                "name": "拾荒者",
                "description": "在廢墟中尋找資源，你的直覺和觀察力異於常人。",
                "recommended_traits": ["scavenger_instinct", "cautious"]
            },
            "drifter": {
                "name": "流浪者",
                "description": "四處漂泊，見識廣泛，你的人生充滿傳奇。",
                "recommended_traits": ["well_traveled", "streetwise"]
            }
        }

        # 背景选择
        bg_choice = st.radio(
            "选择背景",
            list(backgrounds.keys()),
            format_func=lambda x: backgrounds[x]["name"],
            index=["wasteland_doctor", "scavenger", "drifter"].index(st.session_state.char_background_id) if st.session_state.char_background_id in ["wasteland_doctor", "scavenger", "drifter"] else 0,
            key="char_background"
        )

        # 更新 session_state
        st.session_state.char_background_id = bg_choice
        st.session_state.char_background_name = backgrounds[bg_choice]["name"]

        # 显示背景详情
        bg_info = backgrounds[bg_choice]
        with st.expander(f"📖 {bg_info['name']} - 详情 [展开]"):
            st.write(bg_info["description"])
            st.write(f"**推荐特质：** {', '.join(bg_info['recommended_traits'])}")

        st.markdown("---")

        # 角色预览（实时）
        st.markdown("### 👁️ 角色预览")

        # 创建预览状态
        preview_state = CharacterPreviewState(
            name=st.session_state.char_name,
            gender=st.session_state.char_gender,
            profession=st.session_state.char_profession,
            strength=st.session_state.char_strength,
            intelligence=st.session_state.char_intelligence,
            agility=st.session_state.char_agility,
            charisma=st.session_state.char_charisma,
            perception=st.session_state.char_perception,
            endurance=st.session_state.char_endurance,
            background_id= st.session_state.char_background_id,
            background_name=st.session_state.char_background_name,
            positive_traits=list(st.session_state.char_positive_traits),
            negative_traits=list(st.session_state.char_negative_traits),
        )

        # 渲染预览
        render_character_preview_sidebar(preview_state, show_all=False)

        st.markdown("---")

        # 特质选择
        st.markdown("### 🎯 选择特质（可选）")

        # 正面特质
        st.write("**正面特质**（最多 2 个）")
        selected_positive = []
        for trait in positive_traits:
            is_checked = trait in st.session_state.char_positive_traits
            if st.checkbox(trait, value=is_checked, key=f"trait_positive_{trait}"):
                if trait not in st.session_state.char_positive_traits:
                    st.session_state.char_positive_traits.append(trait)
            if is_checked:
                selected_positive.append(trait)

        if len(selected_positive) > 2:
            st.warning("⚠️ 最多选择 2 个正面特质")
            if len(st.session_state.char_positive_traits) > 2:
                st.session_state.char_positive_traits = selected_positive[:2]

        # 负面特质
        st.write("**负面特质**（最多 2 个）")
        selected_negative = []
        for trait in negative_traits:
            is_checked = trait in st.session_state.char_negative_traits
            if st.checkbox(trait, value=is_checked, key=f"trait_negative_{trait}"):
                if trait not in st.session_state.char_negative_traits:
                    st.session_state.char_negative_traits.append(trait)
            if is_checked:
                selected_negative.append(trait)

        if len(selected_negative) > 2:
            st.warning("⚠️ 最多选择 2 个负面特质")
            if len(st.session_state.char_negative_traits) > 2:
                st.session_state.char_negative_traits = selected_negative[:2]

        st.markdown("---")

        # 创建按钮
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ 创建角色", type="primary", key="create_char"):
                # 验证
                if total_points != 20:
                    st.error("❌ 属性总和必须为 20 点")
                    return None

                # 创建角色
                creator = CharacterCreator()
                creator.set_name(name)
                creator.set_gender(gender)
                creator.choose_background(bg_choice)

                # 添加特质
                for trait in selected_positive + selected_negative:
                    creator.add_trait(trait)

                # 分配属性
                creator.distribute_stats({
                    "str": strength,
                    "int": intelligence,
                    "agi": agility,
                    "cha": charisma,
                    "per": perception,
                    "end": endurance,
                })

                # 构建角色（传入选择的职业）
                try:
                    player = creator.build(profession=_get_profession_from_name(profession))
                    st.success(f"🎉 角色创建成功！")
                    st.markdown(f"""
                    ### 角色信息
                    - 姓名：{player.name}
                    - 职业：{player.profession}
                    - 性别：{player.gender}
                    - 等级：{player.level}
                    - HP：{player.hp}/{player.max_hp}
                    - MP：{player.mp}/{player.max_mp}
                    - 金币：{player.gold}
                    """)
                    return player
                except ValueError as e:
                    st.error(f"❌ 创建角色失败：{e}")
                    return None

        with col2:
            if st.button("❌ 取消", key="cancel_char"):
                return None

    with col_preview:
        # 预览面板
        st.markdown("### 👁️ 角色预览")

        # 配置管理
        with st.expander("💾 配置管理", expanded=False):
            render_preset_manager()

        # 创建预览状态
        preview_state = CharacterPreviewState(
            name=st.session_state.char_name,
            gender=st.session_state.char_gender,
            profession=st.session_state.char_profession,
            strength=st.session_state.char_strength,
            intelligence=st.session_state.char_intelligence,
            agility=st.session_state.char_agility,
            charisma=st.session_state.char_charisma,
            perception=st.session_state.char_perception,
            endurance=st.session_state.char_endurance,
            background_id=st.session_state.char_background_id,
            background_name=st.session_state.char_background_name,
            positive_traits=list(st.session_state.char_positive_traits),
            negative_traits=list(st.session_state.char_negative_traits),
        )

        # 渲染预览
        render_character_preview_sidebar(preview_state, show_all=True)

    return None
