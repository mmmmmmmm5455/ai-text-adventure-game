#!/usr/bin/env python
"""测试 Player.create_from_profile() 和 create_from_creator() 方法"""

import sys
from pathlib import Path

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from game.character_creator import CharacterCreator
from game.player import Player, Profession

def test_create_from_profile():
    """测试 create_from_profile 和 create_from_creator 方法"""
    print("🧪 Player.create_from_profile() & create_from_creator() 测试")
    print("=" * 50)

    # 测试 1：创建一个 CharacterCreator
    print("\n📝 测试 1：创建 CharacterCreator")
    try:
        creator = CharacterCreator()
        creator.set_name("测试角色")
        creator.set_gender("男")
        creator.choose_background("wasteland_doctor")
        creator.add_trait("first_aid_master")
        creator.add_trait("calm_minded")

        # 分配属性
        creator.distribute_stats({
            "str": 8,
            "int": 3,
            "agl": 4,
            "cha": 2,
            "per": 2,
            "end": 1,
        })

        print(f"  ✅ CharacterCreator 创建成功")

    except Exception as e:
        print(f"  ❌ CharacterCreator 创建失败：{e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试 2：使用 create_from_creator 创建 Player
    print("\n📝 测试 2：使用 create_from_creator 创建 Player")
    try:
        player = Player.create_from_creator(creator)

        print(f"  ✅ Player 创建成功")
        print(f"     姓名：{player.name}")
        print(f"     职业：{player.profession}")
        print(f"     性别：{player.gender}")
        print(f"     等级：{player.level}")
        print(f"     HP：{player.hp}/{player.max_hp}")
        print(f"     MP：{player.mp}/{player.max_mp}")
        print(f"     金币：{player.gold}")
        print(f"     特质：{player.traits}")
        print(f"     背景：{player.background_name}")
        print(f"     属性：力量={player.strength}, 智力={player.intelligence}")

    except Exception as e:
        print(f"  ❌ Player 创建失败：{e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试 3：验证数据一致性
    print("\n📝 测试 3：验证数据一致性")
    try:
        # 验证属性
        assert player.strength == 8, "力量不一致"
        assert player.intelligence == 3, "智力不一致"
        assert player.agility == 4, "敏捷不一致"
        assert player.charisma == 2, "魅力不一致"
        assert player.perception == 2, "感知不一致"
        assert player.endurance == 1, "耐力不一致"

        # 验证特质
        expected_traits = ["first_aid_master", "calm_minded"]
        assert sorted(player.traits) == sorted(expected_traits), "特质不一致"

        # 验证背景
        assert player.background_name == "廢土醫生", "背景名称不一致"

        print(f"  ✅ 数据一致性验证通过")

    except AssertionError as e:
        print(f"  ❌ 数据一致性验证失败：{e}")
        return False
    except Exception as e:
        print(f"  ❌ 验证过程中出错：{e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试 4：测试不同职业
    print("\n📝 测试 4：测试不同职业的 CharacterCreator")
    profession_map = {
        Profession.WARRIOR: "战士",
        Profession.MAGE: "法师",
        Profession.ROGUE: "盗贼",
        Profession.BARD: "吟游诗人",
    }

    for prof, prof_name in profession_map.items():
        try:
            creator = CharacterCreator()
            creator.set_name(f"{prof_name}测试")
            creator.set_gender("女")
            creator.choose_background("drifter")

            # 简化属性分配（总和 20）
            creator.distribute_stats({
                "str": 5,
                "int": 5,
                "agl": 5,
                "cha": 3,
                "per": 1,
                "end": 1,
            })

            player = Player.create_from_creator(creator)

            print(f"  ✅ {prof_name} - 创建成功")

        except Exception as e:
            print(f"  ❌ {prof_name} - 创建失败：{e}")
            return False

    # 测试 5：测试错误处理
    print("\n📝 测试 5：测试错误处理")
    try:
        # 传入非 CharacterCreator 对象应该抛出 TypeError
        try:
            Player.create_from_creator("not a creator")
            print(f"  ❌ 应该抛出 TypeError")
            return False
        except TypeError as e:
            print(f"  ✅ 正确抛出 TypeError：{e}")

        # 传入 None 应该抛出 TypeError
        try:
            Player.create_from_creator(None)
            print(f"  ❌ 应该抛出 TypeError")
            return False
        except TypeError as e:
            print(f"  ✅ 正确抛出 TypeError：{e}")

    except Exception as e:
        print(f"  ❌ 错误处理测试失败：{e}")
        return False

    print("\n✅ 所有测试通过！")
    return True

if __name__ == "__main__":
    success = test_create_from_profile()
    sys.exit(0 if success else 1)
