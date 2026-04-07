"""
测试角色预览功能
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
    render_preset_manager,
)


def test_character_preview_state():
    """测试角色预览状态"""
    print("=" * 60)
    print("测试 1: 角色预览状态")
    print("=" * 60)

    state = CharacterPreviewState(
        name="测试角色",
        gender="男",
        profession="战士",
        strength=8,
        intelligence=3,
        agility=2,
        charisma=2,
        perception=3,
        endurance=2,
        background_id="wasteland_doctor",
        background_name="廢土醫生",
        positive_traits=["first_aid_master", "calm_minded"],
        negative_traits=["clumsy"],
    )

    print(f"✓ 创建状态对象")
    print(f"  姓名: {state.name}")
    print(f"  职业: {state.profession}")
    print(f"  属性总和: {state.strength + state.intelligence + state.agility + state.charisma + state.perception + state.endurance}")
    print()


def test_preset_management():
    """测试预设管理"""
    print("=" * 60)
    print("测试 2: 预设管理")
    print("=" * 60)

    # 模拟 session_state
    import types
    st_mock = types.SimpleNamespace()
    st_mock.session_state = {}

    # 保存预设
    state1 = CharacterPreviewState(
        name="战士配置",
        profession="战士",
        strength=8,
        intelligence=3,
        agility=2,
        charisma=2,
        perception=3,
        endurance=2,
    )

    save_preset(state1, "战士_标准配置")

    # 保存另一个预设
    state2 = CharacterPreviewState(
        name="法师配置",
        profession="法师",
        strength=3,
        intelligence=8,
        agility=2,
        charisma=3,
        perception=2,
        endurance=2,
    )

    save_preset(state2, "法师_标准配置")

    # 列出预设
    presets = list_presets()
    print(f"✓ 保存预设")
    print(f"  预设列表: {presets}")
    assert len(presets) == 2, f"应该有 2 个预设，实际有 {len(presets)} 个"

    # 加载预设
    loaded = load_preset("战士_标准配置")
    print(f"✓ 加载预设")
    print(f"  加载的预设: {loaded.name}, 职业: {loaded.profession}")
    assert loaded.name == "战士配置"
    assert loaded.profession == "战士"

    # 删除预设
    delete_preset("法师_标准配置")
    presets_after = list_presets()
    print(f"✓ 删除预设")
    print(f"  删除后的预设列表: {presets_after}")
    assert len(presets_after) == 1, f"应该有 1 个预设，实际有 {len(presets_after)} 个"

    print()


def test_preview_comparison():
    """测试预览对比"""
    print("=" * 60)
    print("测试 3: 预览对比")
    print("=" * 60)

    state1 = CharacterPreviewState(
        name="战士",
        profession="战士",
        strength=8,
        intelligence=3,
        agility=2,
        charisma=2,
        perception=3,
        endurance=2,
    )

    state2 = CharacterPreviewState(
        name="法师",
        profession="法师",
        strength=3,
        intelligence=8,
        agility=2,
        charisma=3,
        perception=2,
        endurance=2,
    )

    print(f"✓ 创建对比状态")
    print(f"  配置 A: {state1.name}, 力量: {state1.strength}, 智力: {state1.intelligence}")
    print(f"  配置 B: {state2.name}, 力量: {state2.strength}, 智力: {state2.intelligence}")

    # 计算属性对比
    if state1.strength > state2.strength:
        print(f"  • 力量: {state1.name} 更强（+{state1.strength - state2.strength}）")
    if state2.intelligence > state1.intelligence:
        print(f"  • 智力: {state2.name} 更强（+{state2.intelligence - state1.intelligence}）")

    print()


def test_total_points_calculation():
    """测试属性总和计算"""
    print("=" * 60)
    print("测试 4: 属性总和计算")
    print("=" * 60)

    # 测试正确的配置
    state1 = CharacterPreviewState(
        strength=8,
        intelligence=3,
        agility=2,
        charisma=2,
        perception=3,
        endurance=2,
    )

    total1 = state1.strength + state1.intelligence + state1.agility + state1.charisma + state1.perception + state1.endurance
    print(f"✓ 正确配置（20点）")
    print(f"  属性总和: {total1}")
    assert total1 == 20, f"属性总和应该是 20，实际是 {total1}"

    # 测试超出的配置
    state2 = CharacterPreviewState(
        strength=10,
        intelligence=10,
        agility=10,
        charisma=10,
        perception=10,
        endurance=10,
    )

    total2 = state2.strength + state2.intelligence + state2.agility + state2.charisma + state2.perception + state2.endurance
    print(f"✓ 超出配置（60点）")
    print(f"  属性总和: {total2}, 超出: {total2 - 20}")

    # 测试不足的配置
    state3 = CharacterPreviewState(
        strength=1,
        intelligence=1,
        agility=1,
        charisma=1,
        perception=1,
        endurance=1,
    )

    total3 = state3.strength + state3.intelligence + state3.agility + state3.charisma + state3.perception + state3.endurance
    print(f"✓ 不足配置（6点）")
    print(f"  属性总和: {total3}, 还剩: {20 - total3}")

    print()


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("角色预览功能测试")
    print("=" * 60 + "\n")

    try:
        test_character_preview_state()
        test_preset_management()
        test_preview_comparison()
        test_total_points_calculation()

        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        return True

    except AssertionError as e:
        print("=" * 60)
        print(f"❌ 测试失败: {e}")
        print("=" * 60)
        return False
    except Exception as e:
        print("=" * 60)
        print(f"❌ 测试出错: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
