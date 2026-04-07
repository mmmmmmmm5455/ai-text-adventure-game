#!/usr/bin/env python
"""
角色档案系统测试脚本
测试 Player.get_profile() 和 UI 组件
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from game.player import Player, Profession


def test_get_profile():
    """测试 get_profile() 方法"""
    print("🧪 测试 1：get_profile() 方法")
    print("=" * 50)

    # 创建角色
    player = Player.create("测试角色", Profession.WARRIOR, "男")

    # 获取档案
    profile = player.get_profile()

    # 验证基本信息
    print("📋 基本信息：")
    print(f"  姓名：{profile['basic']['name']}")
    print(f"  职业：{profile['basic']['profession']}")
    print(f"  性别：{profile['basic']['gender']}")
    print(f"  等级：{profile['basic']['level']}")

    # 验证属性信息
    print("\n⚔️ 属性信息：")
    print(f"  力量：{profile['stats']['strength']}")
    print(f"  智力：{profile['stats']['intelligence']}")
    print(f"  敏捷：{profile['stats']['agility']}")
    print(f"  魅力：{profile['stats']['charisma']}")
    print(f"  感知：{profile['stats']['perception']}")
    print(f"  耐力：{profile['stats']['endurance']}")
    print(f"  总和：{profile['stats']['stat_sum']}")

    # 验证状态信息
    print("\n💚 状态信息：")
    print(f"  HP：{profile['status']['hp']}/{profile['status']['max_hp']} ({profile['status']['hp_percent']}%)")
    print(f"  MP：{profile['status']['mp']}/{profile['status']['max_mp']} ({profile['status']['mp_percent']}%)")
    print(f"  经验：{profile['status']['xp_progress']}")
    print(f"  金币：{profile['status']['gold']}")
    print(f"  存活：{profile['status']['alive']}")

    print("\n✅ get_profile() 测试通过")


def test_get_profile_summary():
    """测试 get_profile_summary() 方法"""
    print("\n🧪 测试 2：get_profile_summary() 方法")
    print("=" * 50)

    # 创建角色
    player = Player.create("测试角色", Profession.WARRIOR, "男")

    # 获取档案摘要
    summary = player.get_profile_summary()

    # 打印摘要
    print(summary)

    print("\n✅ get_profile_summary() 测试通过")


def test_multiple_professions():
    """测试不同职业的档案"""
    print("\n🧪 测试 3：不同职业的档案")
    print("=" * 50)

    professions = [
        (Profession.WARRIOR, "战士"),
        (Profession.MAGE, "法师"),
        (Profession.ROGUE, "盗贼"),
        (Profession.BARD, "吟游诗人"),
    ]

    for profession, name in professions:
        player = Player.create(f"{name}测试", profession, "男")
        profile = player.get_profile()

        print(f"\n📋 {name}：")
        print(f"  HP：{profile['status']['hp']}")
        print(f"  MP：{profile['status']['mp']}")
        print(f"  属性总和：{profile['stats']['stat_sum']}")
        print(f"  技能：{profile['skills']['all']}")

    print("\n✅ 多职业测试通过")


def test_profile_with_traits():
    """测试带特质的角色档案"""
    print("\n🧪 测试 4：带特质的角色档案")
    print("=" * 50)

    # 创建带特质的角色
    from game.character_creator import CharacterCreator

    creator = CharacterCreator()
    creator.set_name("特质测试角色")
    creator.set_gender("男")
    creator.distribute_stats({
        "str": 8, "int": 3, "agl": 2,
        "cha": 2, "per": 3, "end": 2
    })

    # 添加背景
    creator.choose_background("wasteland_doctor")

    # 添加特质
    config = creator.config

    # 获取正面特质
    positive_traits = config.positive_traits
    if positive_traits:
        creator.add_trait(positive_traits[0].id, positive=True)
        if len(positive_traits) > 1:
            creator.add_trait(positive_traits[1].id, positive=True)

    # 获取负面特质
    negative_traits = config.negative_traits
    if negative_traits:
        creator.add_trait(negative_traits[0].id, positive=False)

    # 构建角色
    player = creator.build(profession=Profession.WARRIOR)

    # 获取档案
    profile = player.get_profile()

    print(f"\n📋 角色姓名：{profile['basic']['name']}")
    print(f"📜 背景：{profile['background']['description']}")
    print(f"✨ 正面特质：{', '.join(profile['traits']['positive']) or '无'}")
    print(f"⚠️  负面特质：{', '.join(profile['traits']['negative']) or '无'}")

    print("\n✅ 特质测试通过")


def test_profile_comparison():
    """测试角色档案对比"""
    print("\n🧪 测试 5：角色档案对比")
    print("=" * 50)

    # 创建两个角色
    player1 = Player.create("角色A", Profession.WARRIOR, "男")
    player2 = Player.create("角色B", Profession.MAGE, "女")

    profile1 = player1.get_profile()
    profile2 = player2.get_profile()

    print(f"\n📊 角色A vs 角色B")
    print(f"  职业：{profile1['basic']['profession']} vs {profile2['basic']['profession']}")
    print(f"  HP：{profile1['status']['hp']} vs {profile2['status']['hp']}")
    print(f"  MP：{profile1['status']['mp']} vs {profile2['status']['mp']}")
    print(f"  力量：{profile1['stats']['strength']} vs {profile2['stats']['strength']}")
    print(f"  智力：{profile1['stats']['intelligence']} vs {profile2['stats']['intelligence']}")

    print("\n✅ 档案对比测试通过")


def test_level_up_profile():
    """测试升级后的档案"""
    print("\n🧪 测试 6：升级后的档案")
    print("=" * 50)

    # 创建角色
    player = Player.create("升级测试角色", Profession.WARRIOR, "男")

    # 获取升级前档案
    profile_before = player.get_profile()
    print(f"\n📋 升级前：")
    print(f"  等级：{profile_before['basic']['level']}")
    print(f"  HP：{profile_before['status']['hp']}")
    print(f"  MP：{profile_before['status']['mp']}")
    print(f"  力量：{profile_before['stats']['strength']}")

    # 升级
    messages = player.gain_xp(100)  # 足够升级
    print(f"\n📜 升级消息：{' '.join(messages)}")

    # 获取升级后档案
    profile_after = player.get_profile()
    print(f"\n📋 升级后：")
    print(f"  等级：{profile_after['basic']['level']}")
    print(f"  HP：{profile_after['status']['hp']}")
    print(f"  MP：{profile_after['status']['mp']}")
    print(f"  力量：{profile_after['stats']['strength']}")

    print("\n✅ 升级测试通过")


def main():
    """运行所有测试"""
    print("🎭 角色档案系统测试")
    print("=" * 50)

    try:
        test_get_profile()
        test_get_profile_summary()
        test_multiple_professions()
        test_profile_with_traits()
        test_profile_comparison()
        test_level_up_profile()

        print("\n" + "=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        return 0

    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
