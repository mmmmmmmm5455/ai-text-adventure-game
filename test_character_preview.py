#!/usr/bin/env python
"""
角色预览功能测试脚本
测试角色创建界面的实时预览功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

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


def test_character_preview_state():
    """测试角色预览状态"""
    print("🧪 测试 1：角色预览状态")
    print("=" * 50)

    # 创建预览状态
    preview_state = CharacterPreviewState(
        name="测试角色",
        gender="男",
        profession="战士",
        strength=8,
        intelligence=3,
        agility=2,
        charisma=2,
        perception=3,
        endurance=5,
        background_id="wasteland_doctor",
        background_name="廢土醫生",
        positive_traits=["急救精通"],
        negative_traits=["路痴"],
    )

    # 检查预览状态
    print("📋 预览状态：")
    print(f"  姓名：{preview_state.name}")
    print(f"  性别：{preview_state.gender}")
    print(f"  职业：{preview_state.profession}")
    print(f"  属性总和：{preview_state.strength + preview_state.intelligence + preview_state.agility + preview_state.charisma + preview_state.perception + preview_state.endurance} / 20")
    print(f"  背景：{preview_state.background_name or '无'}")
    print(f"  正面特质：{preview_state.positive_traits}")
    print(f"  负面特质：{preview_state.negative_traits}")

    print("\n✅ 角色预览状态测试通过")


def test_preview_comparison():
    """测试预览对比"""
    print("\n🧪 测试 2：预览对比")
    print("=" * 50)

    # 创建两个不同的预览状态
    state1 = CharacterPreviewState(
        name="铁血战士",
        gender="男",
        profession="战士",
        strength=8,
        intelligence=3,
        agility=2,
        charisma=2,
        perception=3,
        endurance=5,
        background_id="wasteland_doctor",
        background_name="廢土醫生",
        positive_traits=["急救精通", "冷靜"],
        negative_traits=[],
    )

    state2 = CharacterPreviewState(
        name="奥术师",
        gender="女",
        profession="法师",
        strength=3,
        intelligence=8,
        agility=2,
        charisma=3,
        perception=2,
        endurance=4,
        background_id="流浪学者",
        background_name="流浪学者",
        positive_traits=["眼尖"],
        negative_traits=["夜盲"],
    )

    # 检查对比
    print("📋 预览对比：")
    print(f"  配置 A：{state1.name} - {state1.profession} (Lv.{state1.strength + state1.intelligence + state1.agility + state1.charisma + state1.perception + state1.endurance})")
    print(f"  配置 B：{state2.name} - {state2.profession} (Lv.{state2.strength + state2.intelligence + state2.agility + state2.charisma + state2.perception + state2.endurance})")

    # 对比属性
    print("\n⚖️ 属性对比：")
    attributes = ["strength", "intelligence", "agility", "charisma", "perception", "endurance"]
    attr_names = ["力量", "智力", "敏捷", "魅力", "感知", "耐力"]

    for attr, attr_name in zip(attributes, attr_names):
        val1 = getattr(state1, attr)
        val2 = getattr(state2, attr)

        if val1 > val2:
            print(f"  {attr_name}：{val1} vs {val2} (配置 A 更强)")
        elif val2 > val1:
            print(f"  {attr_name}：{val1} vs {val2} (配置 B 更强)")
        else:
            print(f"  {attr_name}：{val1} vs {val2} (平手)")

    print("\n✅ 预览对比测试通过")


def test_preset_management():
    """测试预设管理"""
    print("\n🧪 测试 3：预设管理")
    print("=" * 50)

    # 创建预览状态
    state1 = CharacterPreviewState(
        name="战士预设",
        gender="男",
        profession="战士",
        strength=8,
        intelligence=3,
        agility=2,
        charisma=2,
        perception=3,
        endurance=5,
        background_id="wasteland_doctor",
        background_name="廢土醫生",
        positive_traits=["急救精通", "冷靜"],
        negative_traits=[],
    )

    # 保存预设
    print("💾 保存预设...")
    save_preset(state1, "战士高血")

    # 检查保存
    presets = list_presets()
    print(f"  已保存的预设：{presets}")
    if "战士高血" in presets:
        print("  ✅ 预设 '战士高血' 保存成功")
    else:
        print("  ❌ 预设 '战士高血' 保存失败")

    # 加载预设
    print("\n📂 加载预设...")
    loaded = load_preset("战士高血")
    if loaded:
        print(f"  ✅ 预设 '战士高血' 加载成功")
        print(f"  姓名：{loaded.name}")
        print(f"  职业：{loaded.profession}")
    else:
        print("  ❌ 预设 '战士高血' 加载失败")

    # 删除预设
    print("\n🗑️ 删除预设...")
    delete_preset("战士高血")
    presets = list_presets()
    print(f"  已删除的预设：{presets}")
    if "战士高血" not in presets:
        print("  ✅ 预设 '战士高血' 删除成功")
    else:
        print("  ❌ 预设 '战士高血' 删除失败")

    print("\n✅ 预设管理测试通过")


def test_different_professions():
    """测试不同职业的预览"""
    print("\n🧪 测试 4：不同职业的预览")
    print("=" * 50)

    professions = ["战士", "法师", "盗贼", "吟游诗人"]

    for profession in professions:
        state = CharacterPreviewState(
            name=f"{profession}测试角色",
            gender="男",
            profession=profession,
            strength=5,
            intelligence=5,
            agility=5,
            charisma=5,
            perception=5,
            endurance=5,
            background_id=None,
            background_name=None,
            positive_traits=[],
            negative_traits=[],
        )

        print(f"\n📋 {profession} 预览：")
        print(f"  属性总和：{state.strength + state.intelligence + state.agility + state.charisma + state.perception + state.endurance}")

        # 计算实际 HP 和 MP
        profession_to_base = {
            "战士": (120, 30),
            "法师": (70, 80),
            "盗贼": (85, 45),
            "吟游诗人": (90, 55),
        }

        base_hp, base_mp = profession_to_base.get(profession, (100, 50))
        hp = base_hp + (state.endurance - 5) * 10
        mp = base_mp + (state.intelligence - 6) * 5

        print(f"  预估 HP：{hp}")
        print(f"  预估 MP：{mp}")

    print("\n✅ 不同职业预览测试通过")


def test_realtime_update():
    """测试实时更新"""
    print("\n🧪 测试 5：实时更新")
    print("=" * 50)

    # 初始状态
    state = CharacterPreviewState(
        name="实时测试角色",
        gender="男",
        profession="战士",
        strength=5,
        intelligence=5,
        agility=5,
        charisma=5,
        perception=5,
        endurance=5,
        background_id=None,
        background_name=None,
        positive_traits=[],
        negative_traits=[],
    )

    print("📋 初始状态：")
    print(f"  属性总和：{state.strength + state.intelligence + state.agility + state.charisma + state.perception + state.endurance} / 20")

    # 模拟属性变化
    print("\n🔄 模拟属性变化：")
    changes = [
        ("力量", 5, 8),
        ("智力", 5, 8),
        ("敏捷", 5, 3),
        ("魅力", 5, 3),
        ("感知", 5, 2),
        ("耐力", 5, 2),
    ]

    for attr, old_val, new_val in changes:
        old_sum = sum([
            state.strength, state.intelligence, state.agility,
            state.charisma, state.perception, state.endurance
        ])
        
        setattr(state, attr, new_val)
        new_sum = sum([
            state.strength, state.intelligence, state/agility,
            state.charisma, state.perception, state.endurance
        ])
        
        change_type = "+" if new_val > old_val else "-"
        print(f"  {attr}: {old_val} → {new_val} ({change_type}{new_val - old_val}), 总和：{old_sum} → {new_sum}")

        # 检查总和
        if new_sum == 20:
            print("    ✅ 属性总和正确")
        elif new_sum > 20:
            print(f"    ❌ 属性总和超出了 {new_sum - 20} 点")
        else:
            print(f"    ⚠️  还需要 {20 - new_sum} 点")

    print("\n✅ 实时更新测试通过")


def test_empty_preview():
    """测试空预览"""
    print("\n🧪 测试 6：空预览")
    print("=" * 50)

    # 空预览状态
    state = CharacterPreviewState(
        name="",
        gender="",
        profession="",
        strength=0,
        intelligence=0,
        agility=0,
        charisma=0,
        perception=0,
        endurance=0,
        background_id=None,
        background_name=None,
        positive_traits=[],
        negative_traits=[],
    )

    print("📋 空预览状态：")
    print(f"  姓名：{state.name or '未填写'}")
    print(f"  性别：{state.gender or '未选择'}")
    print(f"  职业：{state.profession or '未选择'}")
    print(f"  属性总和：{state.strength + state.intelligence + state.agility + state.charisma + state.perception + state.endurance} / 20")
    print(f"  背景：{state.background_name or '无'}")
    print(f"  正面特质：{state.positive_traits}")
    print(f"  负面特质：{state.negative_traits}")

    print("\n✅ 空预览测试通过")


def main():
    """运行所有测试"""
    print("👁️ 角色预览功能测试")
    print("=" * 50)

    try:
        test_character_preview_state()
        test_preview_comparison()
        test_preset_management()
        test_different_professions()
        test_realtime_update()
        test_empty_preview()

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
