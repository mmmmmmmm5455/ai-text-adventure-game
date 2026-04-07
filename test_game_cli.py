#!/usr/bin/env python3
"""
简单的命令行游戏测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from engine.story_engine import StoryEngine
from game.game_state import GameState
from story.world_config import new_game_state

def main():
    print("🐉 AI 文字冒险游戏 - 命令行测试模式 🐉\n")

    # 创建游戏引擎
    print("正在初始化游戏引擎...")
    engine = StoryEngine()

    # 创建新游戏状态
    print("创建角色...")
    state = new_game_state(
        player_name="测试玩家",
        profession_key="战士",
        gender="男",
    )

    print(f"\n角色创建成功！")
    print(f"名字: {state.player.name}")
    print(f"职业: {state.player.profession.value}")
    print(f"等级: {state.player.level}")
    print(f"HP: {state.player.hp}/{state.player.max_hp}")
    print(f"场景: {state.current_scene_id}")

    print("\n" + "="*50)
    print("生成场景描述...")
    print("="*50)

    # 生成场景描述
    description = engine.generate_scene_description(state)
    print(f"\n{description}")

    print("\n" + "="*50)
    print("生成选项...")
    print("="*50)

    # 生成选项
    choices = engine.generate_choices(state)
    for i, choice in enumerate(choices, 1):
        print(f"{i}. [{choice.choice_id}] {choice.label}")

    print("\n🐉 测试完成！")
    print(f"\n提示: 完整游戏请访问 http://localhost:8502")

if __name__ == "__main__":
    main()
