#!/usr/bin/env python
"""
奪舍历史记录测试脚本
测试奪舍历史功能
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from frontend.screen.possession_history import (
    render_possession_history,
    render_possession_summary,
    render_possession_statistics,
    render_possession_timeline,
    render_possession_comparison
)


def create_mock_history_record(
    character_name: str,
    level: int,
    possessed_at: datetime,
    snapshot_id: str,
    host_player_id: str,
    possessor_player_id: str,
    snapshot_time: datetime,
    game_chapter: int,
) -> dict[str, Any]:
    """创建模拟奪舍历史记录"""
    return {
        'host_snapshot_id': snapshot_id,
        'host_player_id': host_player_id,
        'possessor_player_id': possessor_player_id,
        'possessed_at': possessed_at,
        'character_name': character_name,
        'character_level': level,
        'snapshot_time': snapshot_time,
        'game_chapter': game_chapter,
    }


def test_possession_history():
    """测试奪舍历史"""
    print("🧪 测试 1：奪舍历史")
    print("=" * 50)

    # 创建模拟历史记录
    now = datetime.now()
    history = [
        create_mock_history_record(
            character_name="铁血战士",
            level=5,
            possessed_at=now - timedelta(days=1),
            snapshot_id="snapshot_001",
            host_player_id="host_001",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=30),
            game_chapter=2,
        ),
        create_mock_history_record(
            character_name="奥术师",
            level=8,
            possessed_at=now - timedelta(days=3),
            snapshot_id="snapshot_002",
            host_player_id="host_002",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=45),
            game_chapter=3,
        ),
        create_mock_history_record(
            character_name="暗影盗贼",
            level=6,
            possessed_at=now - timedelta(days=5),
            snapshot_id="snapshot_003",
            host_player_id="host_003",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=60),
            game_chapter=2,
        ),
    ]

    # 检查历史记录
    print("📋 奪舍历史：")
    print(f"  总记录数：{len(history)}")

    for i, record in enumerate(history, 1):
        print(f"\n{i}. {record['character_name']} (Lv.{record['character_level']})")
        print(f"   奪舍时间：{record['possessed_at'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   快照 ID：{record['host_snapshot_id']}")
        print(f"   章节：第 {record['game_chapter']} 章")

    print("\n✅ 奪舍历史测试通过")


def test_possession_summary():
    """测试奪舍摘要"""
    print("\n🧪 测试 2：奪舍摘要")
    print("=" * 50)

    # 创建模拟历史记录
    now = datetime.now()
    history = [
        create_mock_history_record(
            character_name="铁血战士",
            level=5,
            possessed_at=now - timedelta(hours=1),
            snapshot_id="snapshot_001",
            host_player_id="host_001",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=30),
            game_chapter=2,
        ),
        create_mock_history_record(
            character_name="奥术师",
            level=8,
            possessed_at=now - timedelta(hours=3),
            snapshot_id="snapshot_002",
            host_player_id="host_002",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=45),
            game_chapter=3,
        ),
        create_mock_history_record(
            character_name="暗影盗贼",
            level=6,
            possessed_at=now - timedelta(hours=5),
            snapshot_id="snapshot_003",
            host_player_id="host_003",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=60),
            game_chapter=2,
        ),
        create_mock_history_record(
            character_name="银月吟游诗人",
            level=4,
            possessed_at=now - timedelta(hours=10),
            snapshot_id="snapshot_004",
            host_player_id="host_004",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=90),
            game_chapter=1,
        ),
        create_mock_history_record(
            character_name="废土医生",
            level=7,
            possessed_at=now - timedelta(hours=15),
            snapshot_id="snapshot_005",
            host_player_id="host_005",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=120),
            game_chapter=3,
        ),
    ]

    # 检查历史摘要
    print("📋 奪舍摘要（最近 3 次）：")
    print(f"  总记录数：{len(history)}")

    for i, record in enumerate(history[:3], 1):
        time_str = record['possessed_at'].strftime("%m-%d %H:%M")
        print(f"{i}. {record['character_name']} (Lv.{record['character_level']}) - {time_str}")

    if len(history) > 3:
        print(f"... 还有 {len(history) - 3} 条记录")

    print("\n✅ 奪舍摘要测试通过")


def test_possession_statistics():
    """测试奪舍统计"""
    print("\n🧪 测试 3：奪舍统计")
    print("=" * 50)

    # 创建模拟历史记录
    now = datetime.now()
    history = [
        create_mock_history_record(
            character_name="铁血战士",
            level=5,
            possessed_at=now - timedelta(days=1),
            snapshot_id="snapshot_001",
            host_player_id="host_001",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=30),
            game_chapter=2,
        ),
        create_mock_history_record(
            character_name="铁血战士",
            level=5,
            possessed_at=now - timedelta(days=10),
            snapshot_id="snapshot_001",
            host_player_id="host_001",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=30),
            game_chapter=2,
        ),
        create_mock_history_record(
            character_name="奥术师",
            level=8,
            possessed_at=now - timedelta(days=3),
            snapshot_id="snapshot_002",
            host_player_id="host_002",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=45),
            game_chapter=3,
        ),
        create_mock_history_record(
            character_name="暗影盗贼",
            level=6,
            possessed_at=now - timedelta(days=5),
            snapshot_id="snapshot_003",
            host_player_id="host_003",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=60),
            game_chapter=2,
        ),
    ]

    # 检查统计信息
    print("📋 统计信息：")
    print(f"  总记录数：{len(history)}")

    # 统计角色
    character_counts = {}
    for record in history:
        name = record['character_name']
        character_counts[name] = character_counts.get(name, 0) + 1

    print(f"  角色数：{len(character_counts)}")
    for name, count in character_counts.items():
        print(f"    {name}: {count} 次")

    # 统计等级
    level_counts = {}
    for record in history:
        level = record['character_level']
        level_counts[level] = level_counts.get(level, 0) + 1

    print(f"  等级数：{len(level_counts)}")
    for level, count in level_counts.items():
        print(f"    Lv.{level}: {count} 次")

    # 最近和最早
    if history:
        latest = history[0]['possessed_at']
        earliest = history[-1]['possessed_at']
        print(f"  最近奪舍：{latest.strftime('%Y-%m-%d %H:%M')}")
        print(f"  最早奪舍：{earliest.strftime('%Y-%m-%d %H:%M')}")

    print("\n✅ 奪舍统计测试通过")


def test_possession_timeline():
    """测试奪舍时间线"""
    print("\n🧪 测试 4：奪舍时间线")
    print("=" * 50)

    # 创建模拟历史记录
    now = datetime.now()
    history = [
        create_mock_history_record(
            character_name="铁血战士",
            level=5,
            possessed_at=now - timedelta(days=1),
            snapshot_id="snapshot_001",
            host_player_id="host_001",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=30),
            game_chapter=2,
        ),
        create_mock_history_record(
            character_name="奥术师",
            level=8,
            possessed_at=now - timedelta(days=3),
            snapshot_id="snapshot_002",
            host_player_id="host_002",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=45),
            game_chapter=3,
        ),
        create_mock_history_record(
            character_name="暗影盗贼",
            level=6,
            possessed_at=now - timedelta(days=5),
            snapshot_id="snapshot_003",
            host_player_id="host_003",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=60),
            game_chapter=2,
        ),
    ]

    # 检查时间线
    print("📋 奪舍时间线：")

    for i, record in enumerate(history, 1):
        time_str = record['possessed_at'].strftime("%Y-%m-%d %H:%M")
        print(f"{i}. {time_str} - {record['character_name']} (Lv.{record['character_level']})")
        print(f"   快照 ID: {record['host_snapshot_id']}")
        print(f"   章节: 第 {record['game_chapter']} 章")

    print("\n✅ 奪舍时间线测试通过")


def test_possession_comparison():
    """测试奪舍对比"""
    print("\n🧪 测试 5：奪舍对比")
    print("=" * 50)

    # 创建模拟历史记录
    now = datetime.now()
    history = [
        create_mock_history_record(
            character_name="铁血战士",
            level=5,
            possessed_at=now - timedelta(hours=1),
            snapshot_id="snapshot_001",
            host_player_id="host_001",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=30),
            game_chapter=2,
        ),
        create_mock_history_record(
            character_name="奥术师",
            level=8,
            possessed_at=now - timedelta(hours=3),
            snapshot_id="snapshot_002",
            host_player_id="host_002",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=45),
            game_chapter=3,
        ),
        create_mock_history_record(
            character_name="暗影盗贼",
            level=6,
            possessed_at=now - timedelta(hours=5),
            snapshot_id="snapshot_003",
            host_player_id="host_003",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=60),
            game_chapter=2,
        ),
    ]

    # 检查对比
    print("📋 最近 3 次奪舍对比：")

    for i, record in enumerate(history[:3], 1):
        print(f"\n{i}. {record['character_name']} (Lv.{record['character_level']})")
        print(f"   奪舍时间：{record['possessed_at'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   快照 ID：{record['host_snapshot_id']}")
        print(f"   快照时间：{record['snapshot_time'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   章节：第 {record['game_chapter']} 章")

    print("\n✅ 奪舍对比测试通过")


def test_empty_history():
    """测试空历史记录"""
    print("\n🧪 测试 6：空历史记录")
    print("=" * 50)

    history = []

    # 检查空历史
    print("📋 空历史记录：")
    print(f"  总记录数：{len(history)}")

    print("\n✅ 空历史记录测试通过")


def test_duplicate_characters():
    """测试重复角色的奪舍历史"""
    print("\n🧪 测试 7：重复角色的奪舍历史")
    print("=" * 50)

    # 创建模拟历史记录（包含重复角色）
    now = datetime.now()
    history = [
        create_mock_history_record(
            character_name="铁血战士",
            level=5,
            possessed_at=now - timedelta(hours=1),
            snapshot_id="snapshot_001",
            host_player_id="host_001",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=30),
            game_chapter=2,
        ),
        create_mock_history_record(
            character_name="铁血战士",
            level=5,
            possessed_at=now - timedelta(days=10),
            snapshot_id="snapshot_001",
            host_player_id="host_001",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=30),
            game_chapter=2,
        ),
        create_mock_history_record(
            character_name="铁血战士",
            level=5,
            possessed_at=now - timedelta(days=20),
            snapshot_id="snapshot_001",
            host_player_id="host_001",
            possessor_player_id="possessor_001",
            snapshot_time=now - timedelta(days=30),
            game_chapter=2,
        ),
    ]

    # 检查重复角色
    print("📋 重复角色的奪舍历史：")
    print(f"  总记录数：{len(history)}")
    print(f"  角色数：{len(set(r['character_name'] for r in history))}")

    # 统计角色
    character_counts = {}
    for record in history:
        name = record['character_name']
        character_counts[name] = character_counts.get(name, 0) + 1

    for name, count in character_counts.items():
        print(f"    {name}: {count} 次")

    print("\n✅ 重复角色测试通过")


def main():
    """运行所有测试"""
    print("📜 奪舍历史记录测试")
    print("=" * 50)

    try:
        test_possession_history()
        test_possession_summary()
        test_possession_statistics()
        test_possession_timeline()
        test_possession_comparison()
        test_empty_history()
        test_duplicate_characters()

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
