"""
角色档案 UI 组件
显示角色的详细信息
"""

import streamlit as st
from game.player import Player


def render_profile_card(player: Player, show_all: bool = True) -> None:
    """渲染角色档案卡片。

    Args:
        player: Player 对象
        show_all: 是否显示所有信息（包括背包和装备）
    """
    profile = player.get_profile()

    # 标题
    st.markdown(f"## 🎭 {profile['basic']['name']} 的档案")

    # 基本信息
    st.markdown("### 📋 基本信息")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("姓名", profile['basic']['name'])
    with col2:
        st.metric("职业", profile['basic']['profession'])
    with col3:
        st.metric("性别", profile['basic']['gender'])
    with col4:
        st.metric("等级", profile['basic']['level'])

    # 状态信息
    st.markdown("---")
    st.markdown("### 💚 状态")

    # HP 和 MP
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "HP",
            f"{profile['status']['hp']}/{profile['status']['max_hp']}",
            delta=f"{profile['status']['hp_percent']}%",
            delta_color="normal" if profile['status']['alive'] else "inverse"
        )

        # HP 进度条
        st.progress(profile['status']['hp_percent'] / 100)

    with col2:
        st.metric(
            "MP",
            f"{profile['status']['mp']}/{profile['status']['max_mp']}",
            delta=f"{profile['status']['mp_percent']}%"
        )

        # MP 进度条
        st.progress(profile['status']['mp_percent'] / 100)

    # 经验和金币
    col1, col2 = st.columns(2)
    with col1:
        st.metric("经验", profile['status']['xp_progress'])
    with col2:
        st.metric("金币", profile['status']['gold'])

    # 属性信息
    st.markdown("---")
    st.markdown("### ⚔️ 属性")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("力量", profile['stats']['strength'])
        st.metric("智力", profile['stats']['intelligence'])
    with col2:
        st.metric("敏捷", profile['stats']['agility'])
        st.metric("魅力", profile['stats']['charisma'])
    with col3:
        st.metric("感知", profile['stats']['perception'])
        st.metric("耐力", profile['stats']['endurance'])

    st.caption(f"属性总和：{profile['stats']['stat_sum']}/60")

    # 背景信息
    st.markdown("---")
    st.markdown("### 📜 背景")
    st.info(profile['background']['description'])

    # 特质信息
    st.markdown("---")
    st.markdown("### ✨ 特质")

    if profile['traits']['positive']:
        st.success("**正面特质：** " + ", ".join(profile['traits']['positive']))
    else:
        st.caption("正面特质：无")

    if profile['traits']['negative']:
        st.warning("**负面特质：** " + ", ".join(profile['traits']['negative']))
    else:
        st.caption("负面特质：无")

    # 装备信息
    if show_all:
        st.markdown("---")
        st.markdown("### 🛡️ 装备")
        st.info(profile['equipment']['description'])

    # 技能信息
    if show_all:
        st.markdown("---")
        st.markdown("### 🔮 技能")

        if profile['skills']['all']:
            for skill in profile['skills']['all']:
                st.success(f"- {skill}")
        else:
            st.caption("技能：无")

    # 背包信息
    if show_all:
        st.markdown("---")
        st.markdown("### 🎒 背包")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("物品数量", profile['inventory']['items_count'])
        with col2:
            st.metric("背包容量", f"{profile['inventory']['items_count']}/{profile['inventory']['max_slots']}")

        # 列出背包物品
        if player.inventory.items:
            st.markdown("**物品列表：**")
            for item in player.inventory.items[:10]:  # 最多显示 10 个
                st.caption(f"- {item.name} x{item.quantity}")
                if item.description:
                    st.caption(f"  {item.description}")
            if len(player.inventory.items) > 10:
                st.caption(f"... 还有 {len(player.inventory.items) - 10} 个物品")
        else:
            st.caption("背包为空")


def render_profile_summary(player: Player) -> None:
    """渲染角色档案摘要（简洁版）。

    Args:
        player: Player 对象
    """
    profile = player.get_profile()

    # 摘要卡片
    with st.expander(f"📋 {profile['basic']['name']} 的档案", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.caption(f"**职业：** {profile['basic']['profession']}")
            st.caption(f"**等级：** {profile['basic']['level']}")

        with col2:
            st.caption(f"**HP：** {profile['status']['hp']}/{profile['status']['max_hp']}")
            st.caption(f"**MP：** {profile['status']['mp']}/{profile['status']['max_mp']}")

        with col3:
            st.caption(f"**属性：** {profile['stats']['stat_sum']}")
            st.caption(f"**金币：** {profile['status']['gold']}")


def render_profile_comparison(player1: Player, player2: Player) -> None:
    """渲染两个角色的档案对比。

    Args:
        player1: 第一个角色
        player2: 第二个角色
    """
    profile1 = player1.get_profile()
    profile2 = player2.get_profile()

    st.markdown("## 📊 角色对比")

    # 基本信息
    st.markdown("### 📋 基本信息")
    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**角色 A：** {profile1['basic']['name']}")
        st.caption(f"职业：{profile1['basic']['profession']}")
        st.caption(f"等级：{profile1['basic']['level']}")
        st.caption(f"性别：{profile1['basic']['gender']}")

    with col2:
        st.info(f"**角色 B：** {profile2['basic']['name']}")
        st.caption(f"职业：{profile2['basic']['profession']}")
        st.caption(f"等级：{profile2['basic']['level']}")
        st.caption(f"性别：{profile2['basic']['gender']}")

    # 属性对比
    st.markdown("---")
    st.markdown("### ⚔️ 属性对比")

    stats = ['力量', '智力', '敏捷', '魅力', '感知', '耐力']
    stat_keys = ['strength', 'intelligence', 'agility', 'charisma', 'perception', 'endurance']

    for stat_name, stat_key in zip(stats, stat_keys):
        val1 = profile1['stats'][stat_key]
        val2 = profile2['stats'][stat_key]

        if val1 > val2:
            st.success(f"**{stat_name}：** {val1} vs {val2} (角色 A 更强)")
        elif val2 > val1:
            st.error(f"**{stat_name}：** {val1} vs {val2} (角色 B 更强)")
        else:
            st.caption(f"**{stat_name}：** {val1} vs {val2} (平手)")

    # 状态对比
    st.markdown("---")
    st.markdown("### 💚 状态对比")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**角色 A HP：** {profile1['status']['hp']}/{profile1['status']['max_hp']}")
        st.info(f"**角色 A MP：** {profile1['status']['mp']}/{profile1['status']['max_mp']}")
        st.info(f"**角色 A 金币：** {profile1['status']['gold']}")

    with col2:
        st.info(f"**角色 B HP：** {profile2['status']['hp']}/{profile2['status']['max_hp']}")
        st.info(f"**角色 B MP：** {profile2['status']['mp']}/{profile2['status']['max_mp']}")
        st.info(f"**角色 B 金币：** {profile2['status']['gold']}")
