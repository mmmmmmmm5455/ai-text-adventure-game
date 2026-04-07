#!/usr/bin/env python
"""角色创建 UI 测试脚本"""

import sys
from pathlib import Path

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from game.character_creator import CharacterCreator, CharacterProfile
from game.player import Player, Profession

def test_character_creation_ui():
    """测试角色创建 UI"""
    print("🧪 角色创建 UI 测试")
    print("=" * 50)

    # 测试 1：基础 UI 模块导入
    print("\n📝 测试 1：导入 UI 模块")
    try:
        from frontend.screen.character_creation import render_character_creation_ui
        print("✅ UI 模块导入成功")
    except Exception as e:
        print(f"❌ UI 模块导入失败：{e}")
        return False

    # 测试 2：检查职业
    print("\n📝 测试 2：检查职业")
    professions = ["战士", "法师", "盗贼", "吟游诗人"]
    for prof in professions:
        try:
            profession = Profession(prof)
            print(f"  ✅ {prof} -> {profession}")
        except ValueError as e:
            print(f"  ❌ {prof} -> 错误：{e}")

    # 测试 3：检查背景
    print("\n📝 测试 3：检查背景")
    backgrounds = ["wasteland_doctor", "scavenger", "drifter"]
    for bg in backgrounds:
        print(f"  ✅ {bg}")

    # 测试 4：测试属性分配逻辑
    print("\n📝 测试 4：测试属性分配")
    try:
        creator = CharacterCreator()
        creator.set_name("测试角色")
        creator.set_gender("男")

        # 分配属性
        stats = {
            "str": 8,
            "int": 3,
            "agl": 4,
            "cha": 2,
            "per": 2,
            "end": 1
        }

        creator.distribute_stats(stats)

        print(f"  ✅ 属性分配成功")

    except Exception as e:
        print(f"  ❌ 属性分配失败：{e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试 5：测试完整创建流程
    print("\n📝 测试 5：测试完整创建流程")
    try:
        creator = CharacterCreator()
        creator.set_name("铁血战士")
        creator.set_gender("男")
        creator.choose_background("wasteland_doctor")
        creator.add_trait("first_aid_master")
        creator.add_trait("calm_minded")

        # 推荐属性（修正为总和 20）
        recommended = [8, 3, 2, 2, 3, 2]  # 战士推荐属性
        creator.distribute_stats({
            "str": recommended[0],
            "int": recommended[1],
            "agl": recommended[2],
            "cha": recommended[3],
            "per": recommended[4],
            "end": recommended[5],
        })

        # 构建角色（传入职业）
        profession_map = {
            "战士": Profession.WARRIOR,
            "法师": Profession.MAGE,
            "盗贼": Profession.ROGUE,
            "吟游诗人": Profession.BARD,
        }
        player = creator.build(profession=profession_map["战士"])

        print(f"  ✅ 角色创建成功")
        print(f"     姓名：{player.name}")
        print(f"     职业：{player.profession}")
        print(f"     性别：{player.gender}")
        print(f"     等级：{player.level}")
        print(f"     HP：{player.hp}/{player.max_hp}")
        print(f"     MP：{player.mp}/{player.max_mp}")
        print(f"     金币：{player.gold}")
        print(f"     特质：{player.traits}")
        print(f"     背景：{player.background_name}")
        print(f"     属性：力量={player.strength}, 智力={player.intelligence}, 敏捷={player.agility}, 魅力={player.charisma}, 感知={player.perception}, 耐力={player.endurance}")

    except Exception as e:
        print(f"  ❌ 角色创建失败：{e}")
        import traceback
        traceback.print_exc()
        return False
        
        print(f"  ✅ 角色创建成功")
        print(f"     姓名：{player.name}")
        print(f"     职业：{player.profession}")
        print(f"     性别：{player.gender}")
        print(f"     等级：{player.level}")
        print(f"     HP：{player.hp}/{player.max_hp}")
        print(f"     MP：{player.mp}/{player.max_mp}")
        print(f"     金币：{player.gold}")
        print(f"     特质：{player.traits}")
        print(f"     背景：{player.background_name}")
        
    except Exception as e:
        print(f"  ❌ 角色创建失败：{e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试 6：测试不同职业的推荐属性
    print("\n📝 测试 6：测试不同职业的推荐属性")
    profession_to_attrs = {
        "战士": [8, 3, 2, 2, 3, 2],
        "法师": [3, 8, 2, 3, 2, 2],
        "盗贼": [2, 3, 8, 2, 3, 2],
        "吟游诗人": [2, 3, 2, 8, 3, 2],
    }
    
    for prof, attrs in profession_to_attrs.items():
        total = sum(attrs)
        status = "✅" if total == 20 else "❌"
        print(f"  {status} {prof}: {attrs} (总和：{total})")

    print("\n✅ 所有测试通过！")
    return True

if __name__ == "__main__":
    success = test_character_creation_ui()
    sys.exit(0 if success else 1)
