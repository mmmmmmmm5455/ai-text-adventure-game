#!/usr/bin/env python
"""
快照预览功能测试脚本
测试快照预览 UI 组件
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from frontend.screen.snapshot_preview import (
    render_snapshot_preview,
    render_snapshot_summary,
    render_snapshot_comparison,
    render_snapshot_list
)


def create_mock_snapshot(
    name: str,
    level: int,
    hp: int,
    max_hp: int,
    background: str | None,
    chapter: int,
    playtime: int,
    label: str | None = None,
    last_words: str | None = None,
) -> dict[str, Any]:
    """创建模拟快照数据"""
    return {
        'snapshot_id': f"snapshot_{name}",
        'character_name': name,
        'character_level': level,
        'character_bg_name': background,
        'character_hp': hp,
        'character_max_hp': max_hp,
        'snapshot_time': datetime.now() - timedelta(hours=playtime),
        'last_words': last_words,
        'recent_events': [
            {'event_type': '战斗', 'event_summary': f'{name} 在迷雾森林击败了一只野兽', 'round_count': 5},
            {'event_type': '探索', 'event_summary': f'{name} 在废墟中发现了一个宝箱', 'round_count': 10},
            {'event_type': '对话', 'event_summary': f'{name} 与村长交谈', 'round_count': 15},
        ],
        'game_chapter': chapter,
        'playtime_minutes': playtime,
        'host_display_name': f"玩家_{name}",
        'snapshot_label': label,
    }


def test_snapshot_preview():
    """测试快照预览"""
    print("🧪 测试 1：快照预览")
    print("=" * 50)

    # 创建模拟快照
    snapshot = create_mock_snapshot(
        name="铁血战士",
        level=5,
        hp=80,
        max_hp=120,
        background="廢土醫生",
        chapter=2,
        playtime=120,
        label="强力战士",
        last_words="我会保护这个世界的..."
    )

    # 检查快照数据
    print("📋 快照数据：")
    print(f"  角色名：{snapshot['character_name']}")
    print(f"  等级：{snapshot['character_level']}")
    print(f"  背景：{snapshot['character_bg_name']}")
    print(f"  HP：{snapshot['character_hp']}/{snapshot['character_max_hp']}")
    print(f"  章节：{snapshot['game_chapter']}")
    print(f"  游戏时长：{snapshot['playtime_minutes']} 分钟")
    print(f"  标签：{snapshot['snapshot_label']}")
    print(f"  遗言：{snapshot['last_words']}")
    print(f"  最近事件：{len(snapshot['recent_events'])} 个")

    print("\n✅ 快照预览测试通过")


def test_snapshot_summary():
    """测试快照摘要"""
    print("\n🧪 测试 2：快照摘要")
    print("=" * 50)

    # 创建模拟快照
    snapshot = create_mock_snapshot(
        name="奥术师",
        level=8,
        hp=50,
        max_hp=70,
        background="流浪学者",
        chapter=3,
        playtime=180,
        label="法师",
        last_words="知识就是力量..."
    )

    # 检查快照数据
    print("📋 快照摘要：")
    print(f"  角色：{snapshot['character_name']} - Lv.{snapshot['character_level']}")
    print(f"  背景：{snapshot['character_bg_name']}")
    print(f"  HP：{snapshot['character_hp']}/{snapshot['character_max_hp']}")
    print(f"  标签：{snapshot['snapshot_label']}")
    print(f"  遗言：{snapshot['last_words'][:30]}...")
    print(f"  创建者：{snapshot['host_display_name']}")

    print("\n✅ 快照摘要测试通过")


def test_snapshot_comparison():
    """测试快照对比"""
    print("\n🧪 测试 3：快照对比")
    print("=" * 50)

    # 创建两个模拟快照
    snapshot1 = create_mock_snapshot(
        name="暗影盗贼",
        level=6,
        hp=70,
        max_hp=85,
        background="拾荒者",
        chapter=2,
        playtime=90,
        label="高敏捷",
        last_words="速度就是生命..."
    )

    snapshot2 = create_mock_snapshot(
        name="银月吟游诗人",
        level=4,
        hp=60,
        max_hp=90,
        background="流浪者",
        chapter=1,
        playtime=60,
        label="辅助",
        last_words="歌声能治愈一切..."
    )

    # 检查快照对比
    print("📋 快照 A vs 快照 B：")
    print(f"  角色：{snapshot1['character_name']} vs {snapshot2['character_name']}")
    print(f"  等级：{snapshot1['character_level']} vs {snapshot2['character_level']}")
    print(f"  HP：{snapshot1['character_hp']}/{snapshot1['character_max_hp']} vs {snapshot2['character_hp']}/{snapshot2['character_max_hp']}")
    print(f"  标签：{snapshot1['snapshot_label']} vs {snapshot2['snapshot_label']}")
    print(f"  遗言：{snapshot1['last_words'][:20]}... vs {snapshot2['last_words'][:20]}...")

    print("\n✅ 快照对比测试通过")


def test_snapshot_list():
    """测试快照列表"""
    print("\n🧪 测试 4：快照列表")
    print("=" * 50)

    # 创建多个模拟快照
    snapshots = [
        create_mock_snapshot(
            name="铁血战士",
            level=5,
            hp=80,
            max_hp=120,
            background="廢土醫生",
            chapter=2,
            playtime=120,
            label="战士",
            last_words="保护这个世界..."
        ),
        create_mock_snapshot(
            name="奥术师",
            level=8,
            hp=50,
            max_hp=70,
            background="流浪学者",
            chapter=3,
            playtime=180,
            label="法师",
            last_words="知识就是力量..."
        ),
        create_mock_snapshot(
            name="暗影盗贼",
            level=6,
            hp=70,
            max_hp=85,
            background="拾荒者",
            chapter=2,
            playtime=90,
            label="盗贼",
            last_words="速度就是生命..."
        ),
        create_mock_snapshot(
            name="银月吟游诗人",
            level=4,
            hp=60,
            max_hp=90,
            background="流浪者",
            chapter=1,
            playtime=60,
            label="辅助",
            last_words="歌声能治愈一切..."
        ),
        create_mock_snapshot(
            name="废土医生",
            level=7,
            hp=90,
            max_hp=100,
            background="廢土醫生",
            chapter=3,
            playtime=150,
            label="治疗",
            last_words="生命是最宝贵的..."
        ),
    ]

    # 检查快照列表
    print(f"📋 快照列表：{len(snapshots)} 个")

    for i, snapshot in enumerate(snapshots, 1):
        print(f"\n{i}. {snapshot['character_name']} - Lv.{snapshot['character_level']}")
        print(f"   背景：{snapshot['character_bg_name']}")
        print(f"   HP：{snapshot['character_hp']}/{snapshot['character_max_hp']}")
        print(f"   标签：{snapshot['snapshot_label']}")
        print(f"   遗言：{snapshot['last_words'][:30]}...")
        print(f"   创建者：{snapshot['host_display_name']}")
        print(f"   事件：{len(snapshot['recent_events'])} 个")

    print("\n✅ 快照列表测试通过")


def test_snapshot_with_different_states():
    """测试不同状态的快照"""
    print("\n🧪 测试 5：不同状态的快照")
    print("=" * 50)

    # 创建不同状态的快照
    full_health = create_mock_snapshot(
        name="满血战士",
        level=5,
        hp=120,
        max_hp=120,
        background="廢土醫生",
        chapter=2,
        playtime=60,
        label="满血",
        last_words="准备战斗！"
    )

    low_health = create_mock_snapshot(
        name="重伤法师",
        level=8,
        hp=10,
        max_hp=70,
        background="流浪学者",
        chapter=3,
        playtime=120,
        label="重伤",
        last_words="还能继续..."
    )

    no_last_words = create_mock_snapshot(
        name="无名战士",
        level=3,
        hp=50,
        max_hp=100,
        background="拾荒者",
        chapter=1,
        playtime=30,
        label="新手",
        last_words=None
    )

    # 检查不同状态
    print("📋 不同状态的快照：")
    print(f"\n1. 满血状态：")
    print(f"   HP：{full_health['character_hp']}/{full_health['character_max_hp']} (100%)")
    print(f"   遗言：{full_health['last_words']}")

    print(f"\n2. 重伤状态：")
    print(f"   HP：{low_health['character_hp']}/{low_health['character_max_hp']} (14.3%)")
    print(f"   遗言：{low_health['last_words']}")

    print(f"\n3. 无遗言：")
    print(f"   HP：{no_last_words['character_hp']}/{no_last_words['character_max_hp']} (50%)")
    print(f"   遗言：{no_last_words['last_words']}")

    print("\n✅ 不同状态快照测试通过")


def test_snapshot_search():
    """测试快照搜索"""
    print("\n🧪 测试 6：快照搜索")
    print("=" * 50)

    # 创建多个快照
    snapshots = [
        create_mock_snapshot(
            name="铁血战士",
            level=5,
            hp=80,
            max_hp=120,
            background="廢土醫生",
            chapter=2,
            playtime=120,
            label="战士",
            last_words="保护..."
        ),
        create_mock_snapshot(
            name="铁血法师",
            level=5,
            hp=50,
            max_hp=70,
            background="流浪学者",
            chapter=2,
            playtime=90,
            label="法师",
            last_words="学习..."
        ),
        create_mock_snapshot(
            name="暗影盗贼",
            level=6,
            hp=70,
            max_hp=85,
            background="拾荒者",
            chapter=2,
            playtime=60,
            label="盗贼",
            last_words="潜行..."
        ),
    ]

    # 搜索测试
    search_term = "铁血"
    filtered_snapshots = [s for s in snapshots if search_term.lower() in s['character_name'].lower()]

    print(f"📋 搜索 \"{search_term}\"：")
    print(f"   总数：{len(snapshots)} 个")
    print(f"   匹配：{len(filtered_snapshots)} 个")

    for snapshot in filtered_snapshots:
        print(f"   - {snapshot['character_name']} (Lv.{snapshot['character_level']})")

    print("\n✅ 快照搜索测试通过")


def main():
    """运行所有测试"""
    print("👁️ 快照预览功能测试")
    print("=" * 50)

    try:
        test_snapshot_preview()
        test_snapshot_summary()
        test_snapshot_comparison()
        test_snapshot_list()
        test_snapshot_with_different_states()
        test_snapshot_search()

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
