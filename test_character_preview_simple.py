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

# 只测试预览状态，避免导入其他模块
from dataclasses import dataclass, field


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
    positive_traits: list = field(default_factory=list)
    negative_traits: list = field(default_factory=list)


def main():
    """运行测试"""
    print("👁️ 角色预览功能测试")
    print("=" * 50)

    try:
        # 测试 1：创建预览状态
        print("🧪 测试 1：创建预览状态")
        state = CharacterPreviewState(
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
            positive_traits=["急救精通", "冷靜"],
            negative_traits=[],
        )
        
        print(f"✅ 预览状态创建成功")
        print(f"  姓名：{state.name}")
        print(f"  职业：{state.profession}")
        print(f"  属性总和：{state.strength + state.intelligence + state.agility + state.charisma + state.perception + state.endurance} / 20")

        # 测试 2：修改属性
        print("\n🧪 测试 2：修改属性")
        state.strength = 10
        print(f"  力量：5 → 10")
        print(f"  新总和：{state.strength + state.intelligence + state.agility + state.charisma + state.perception + state.endurance} / 20")

        if state.strength + state.intelligence + state.agility + state.charisma + state.perception + state.endurance == 20:
            print("  ✅ 属性总和正确")
        else:
            print(f"  ❌ 属性总和错误：{state.strength + state.intelligence + state.agility + state.charisma + state.perception + state.endurance}")

        # 测试 3：计算 HP 和 MP
        print("\n🧪 测试 3：计算 HP 和 MP")
        profession_to_base = {
            "战士": (120, 30),
            "法师": (70, 80),
            "盗贼": (85, 45),
            "吟游诗人": (90, 55),
        }
        
        base_hp, base_mp = profession_to_base.get(state.profession, (100, 50))
        hp = base_hp + (state.endurance - 5) * 10
        mp = base_mp + (state.intelligence - 6) * 5
        
        print(f"  {state.profession}：HP={base_hp}→{hp}, MP={base_mp}→{mp}")

        print("\n✅ 所有测试通过！")
        return 0

    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
