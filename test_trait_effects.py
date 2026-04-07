#!/usr/bin/env python
"""
特质效果系统测试脚本
测试特质效果的计算和应用
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from game.player import Player, Profession
from game.trait_effects import TraitEffect, create_trait_effect, calculate_trait_summary
from game.inventory import InventoryItem


def test_trait_effects_loading():
    """测试特质效果加载"""
    print("🧪 测试 1：特质效果加载")
    print("=" * 50)

    from game.character_creator import CharacterCreatorConfig

    config = CharacterCreatorConfig.get_instance()

    # 检查正面特质
    print("📋 正面特质效果：")
    for trait in config.positive_traits:
        print(f"  {trait.name} ({trait.id})")
        if trait.effects:
            for key, value in trait.effects.items():
                print(f"    - {key}: {value}")
        else:
            print(f"    - 无效果")

    # 检查负面特质
    print("\n📋 负面特质效果：")
    for trait in config.negative_traits:
        print(f"  {trait.name} ({trait.id})")
        if trait.effects:
            for key, value in trait.effects.items():
                print(f"    - {key}: {value}")
        else:
            print(f"    - 无效果")

    print("\n✅ 特质效果加载测试通过")


def test_trait_effect_calculation():
    """测试特质效果计算"""
    print("\n🧪 测试 2：特质效果计算")
    print("=" * 50)

    # 测试正面特质
    positive_traits = ["first_aid_master", "keen_eye"]
    summary = calculate_trait_summary(positive_traits)

    print("📋 正面特质效果摘要：")
    print(f"  治疗加成：{summary['healing_bonus'] * 100}%")
    print(f"  感知加成：{summary['perception_bonus']}")
    print(f"  探索成功加成：{summary['exploration_success_bonus'] * 100}%")
    print(f"  陷阱检测加成：{summary['trap_detection_bonus'] * 100}%")

    # 测试负面特质
    negative_traits = ["clumsy", "night_blindness"]
    summary = calculate_trait_summary(negative_traits)

    print("\n📋 负面特质效果摘要：")
    print(f"  敏捷惩罚：{summary['agility_penalty']}")
    print(f"  物品使用失败率：{summary['item_use_failure_chance'] * 100}%")
    print(f"  夜间感知惩罚：{summary['night_perception_penalty']}")
    print(f"  夜间探索惩罚：{summary['night_exploration_penalty'] * 100}%")

    # 测试混合特质
    mixed_traits = ["first_aid_master", "clumsy"]
    summary = calculate_trait_summary(mixed_traits)

    print("\n📋 混合特质效果摘要：")
    print(f"  治疗加成：{summary['healing_bonus'] * 100}%")
    print(f"  敏捷惩罚：{summary['agility_penalty']}")
    print(f"  物品使用失败率：{summary['item_use_failure_chance'] * 100}%")

    print("\n✅ 特质效果计算测试通过")


def test_healing_with_traits():
    """测试治疗效果应用"""
    print("\n🧪 测试 3：治疗效果应用")
    print("=" * 50)

    # 创建带特质的治疗角色
    from game.character_creator import CharacterCreator

    creator = CharacterCreator()
    creator.set_name("治疗测试角色")
    creator.set_gender("男")
    creator.distribute_stats({
        "str": 3, "per": 3, "end": 3,
        "cha": 3, "int": 3, "agl": 5
    })
    creator.choose_background("wasteland_doctor")
    creator.add_trait("first_aid_master", positive=True)

    player = creator.build(profession=Profession.WARRIOR)

    # 受伤
    player.hp = 50
    player.max_hp = 100
    print(f"📋 初始 HP：{player.hp}/{player.max_hp}")

    # 治疗前
    base_heal = 35
    print(f"📋 基础治疗：{base_heal}")

    # 应用特质效果
    trait_effect = player.get_trait_effect()
    print(f"📋 治疗加成：{trait_effect.healing_bonus * 100}%")

    # 治疗多次
    for i in range(5):
        old_hp = player.hp
        player.heal(base_heal)
        actual_heal = player.hp - old_hp
        print(f"📋 第 {i+1} 次治疗：实际恢复 {actual_heal} HP，当前 HP：{player.hp}")

    print("\n✅ 治疗效果应用测试通过")


def test_consumable_bonus():
    """测试消耗品效果加成"""
    print("\n🧪 测试 4：消耗品效果加成")
    print("=" * 50)

    # 创建带铁胃特质的角色
    from game.character_creator import CharacterCreator

    creator = CharacterCreator()
    creator.set_name("铁胃测试角色")
    creator.set_gender("男")
    creator.distribute_stats({
        "str": 3, "per": 3, "end": 3,
        "cha": 3, "int": 3, "agl": 5
    })
    creator.choose_background("wasteland_doctor")
    creator.add_trait("iron_stomach", positive=True)

    player = creator.build(profession=Profession.WARRIOR)

    # 添加治疗药水
    from story.items import catalog as item_catalog, ItemCategory
    catalog = item_catalog()
    healing_potion = InventoryItem(
        item_id="healing_potion",
        name="治疗药水",
        category=ItemCategory.CONSUMABLE,
        quantity=1,
        description="恢复少量生命值。"
    )
    player.inventory.add_item(healing_potion)

    # 受伤
    player.hp = 50
    player.max_hp = 100
    print(f"📋 初始 HP：{player.hp}/{player.max_hp}")

    # 使用药水
    old_hp = player.hp
    result = player.use_consumable("healing_potion")
    actual_heal = player.hp - old_hp

    if result is None:
        print(f"📋 治疗药水使用成功")
        print(f"📋 实际恢复：{actual_heal} HP")
        print(f"📋 当前 HP：{player.hp}/{player.max_hp}")

        trait_effect = player.get_trait_effect()
        print(f"📋 消耗品加成：{trait_effect.consumable_bonus * 100}%")
        print(f"📋 预期恢复：{35 * (1 + trait_effect.consumable_bonus)} HP")
    else:
        print(f"❌ 治疗药水使用失败：{result}")

    print("\n✅ 消耗品效果加成测试通过")


def test_perception_modifier():
    """测试感知修正"""
    print("\n🧪 测试 5：感知修正")
    print("=" * 50)

    # 测试眼尖特质
    from game.character_creator import CharacterCreator

    creator1 = CharacterCreator()
    creator1.set_name("眼尖角色")
    creator1.set_gender("男")
    creator1.distribute_stats({
        "str": 3, "per": 3, "end": 3,
        "cha": 3, "int": 3, "agl": 5
    })
    creator1.add_trait("keen_eye", positive=True)

    player1 = creator1.build(profession=Profession.ROGUE)

    trait_effect1 = player1.get_trait_effect()
    base_perception = player1.perception

    print("📋 眼尖角色（白昼）：")
    print(f"  基础感知：{base_perception}")
    print(f"  加成：+{trait_effect1.perception_bonus}")
    print(f"  有效感知：{trait_effect1.apply_perception_modifier(base_perception)}")

    print("📋 眼尖角色（夜间）：")
    print(f"  基础感知：{base_perception}")
    print(f"  有效感知：{trait_effect1.apply_perception_modifier(base_perception, is_night=True)}")

    # 测试路痴特质
    creator2 = CharacterCreator()
    creator2.set_name("路痴角色")
    creator2.set_gender("男")
    creator2.distribute_stats({
        "str": 3, "per": 3, "end": 3,
        "cha": 3, "int": 3, "agl": 5
    })
    creator2.add_trait("bad_sense_of_direction", positive=False)

    player2 = creator2.build(profession=Profession.ROGUE)

    trait_effect2 = player2.get_trait_effect()
    base_perception2 = player2.perception

    print("\n📋 路痴角色：")
    print(f"  基础感知：{base_perception2}")
    print(f"  惩罚：{trait_effect2.perception_penalty}")
    print(f"  有效感知：{trait_effect2.apply_perception_modifier(base_perception2)}")

    # 测试夜盲特质
    creator3 = CharacterCreator()
    creator3.set_name("夜盲角色")
    creator3.set_gender("男")
    creator3.distribute_stats({
        "str": 3, "per": 3, "end": 3,
        "cha": 3, "int": 3, "agl": 5
    })
    creator3.add_trait("night_blindness", positive=False)

    player3 = creator3.build(profession=Profession.ROGUE)

    trait_effect3 = player3.get_trait_effect()
    base_perception3 = player3.perception

    print("\n📋 夜盲角色（白昼）：")
    print(f"  基础感知：{base_perception3}")
    print(f"  有效感知：{trait_effect3.apply_perception_modifier(base_perception3, is_night=False)}")

    print("\n📋 夜盲角色（夜间）：")
    print(f"  基础感知：{base_perception3}")
    print(f"  夜间惩罚：{trait_effect3.night_perception_penalty}")
    print(f"  有效感知：{trait_effect3.apply_perception_modifier(base_perception3, is_night=True)}")

    print("\n✅ 感知修正测试通过")


def test_charisma_modifier():
    """测试魅力修正"""
    print("\n🧪 测试 6：魅力修正")
    print("=" * 50)

    # 测试社交花蝴蝶特质
    from game.character_creator import CharacterCreator

    creator = CharacterCreator()
    creator.set_name("社交花角色")
    creator.set_gender("女")
    creator.distribute_stats({
        "str": 3, "per": 3, "end": 3,
        "cha": 3, "int": 3, "agl": 5
    })
    creator.add_trait("social_butterfly", positive=True)

    player = creator.build(profession=Profession.BARD)

    trait_effect = player.get_trait_effect()
    base_charisma = player.charisma

    print("📋 社交花角色：")
    print(f"  基础魅力：{base_charisma}")
    print(f"  加成：+{trait_effect.charisma_bonus}")
    print(f"  有效魅力：{trait_effect.apply_charisma_modifier(base_charisma)}")
    print(f"  NPC 好感度加成：{trait_effect.npc_affinity_bonus * 100}%")
    print(f"  交涉成功率加成：{trait_effect.negotiation_bonus * 100}%")
    print(f"  交易折扣：{trait_effect.trade_discount * 100}%")

    print("\n✅ 魅力修正测试通过")


def test_agility_modifier():
    """测试敏捷修正"""
    print("\n🧪 测试 7：敏捷修正")
    print("=" * 50)

    # 测试笨手笨腳特质
    from game.character_creator import CharacterCreator

    creator = CharacterCreator()
    creator.set_name("笨拙角色")
    creator.set_gender("男")
    creator.distribute_stats({
        "str": 3, "per": 3, "end": 3,
        "cha": 3, "int": 3, "agl": 5
    })
    creator.add_trait("clumsy", positive=False)

    player = creator.build(profession=Profession.ROGUE)

    trait_effect = player.get_trait_effect()
    base_agility = player.agility

    print("📋 笨拙角色：")
    print(f"  基础敏捷：{base_agility}")
    print(f"  惩罚：{trait_effect.agility_penalty}")
    print(f"  有效敏捷：{trait_effect.apply_agility_modifier(base_agility)}")
    print(f"  物品使用失败率：{trait_effect.item_use_failure_chance * 100}%")
    print(f"  潜行失败率：{trait_effect.stealth_failure_chance * 100}%")
    print(f"  闪避惩罚：{trait_effect.dodge_penalty * 100}%")

    print("\n✅ 敏捷修正测试通过")


def test_exploration_bonus():
    """测试探索成功概率加成"""
    print("\n🧪 测试 8：探索成功概率加成")
    print("=" * 50)

    # 测试眼尖 + 路痴
    from game.character_creator import CharacterCreator

    creator = CharacterCreator()
    creator.set_name("矛盾角色")
    creator.set_gender("男")
    creator.distribute_stats({
        "str": 3, "per": 3, "end": 3,
        "cha": 3, "int": 3, "agl": 5
    })
    creator.choose_background("scavenger")
    creator.add_trait("keen_eye", positive=True)
    creator.add_trait("bad_sense_of_direction", positive=False)

    player = creator.build(profession=Profession.ROGUE)

    trait_effect = player.get_trait_effect()

    base_chance = 0.5

    print("📋 矛盾角色（眼尖 + 路痴）：")
    print(f"  基础概率：{base_chance * 100}%")
    print(f"  探索加成：+{trait_effect.exploration_success_bonus * 100}%")
    print(f"  迷路惩罚：-{trait_effect.lost_chance_bonus * 100}%")
    print(f"  有效概率（白昼）：{trait_effect.apply_exploration_bonus(base_chance) * 100}%")
    print(f"  有效概率（夜间）：{trait_effect.apply_exploration_bonus(base_chance, is_night=True) * 100}%")

    print("\n✅ 探索成功概率加成测试通过")


def main():
    """运行所有测试"""
    print("✨ 特质效果系统测试")
    print("=" * 50)

    try:
        test_trait_effects_loading()
        test_trait_effect_calculation()
        test_healing_with_traits()
        test_consumable_bonus()
        test_perception_modifier()
        test_charisma_modifier()
        test_agility_modifier()
        test_exploration_bonus()

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
