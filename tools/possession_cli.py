#!/usr/bin/env python3
"""
奪舍系统命令行工具 - 离线模式
当无法连接数据库时使用
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from game.possession_offline import (
    get_offline_snapshots,
    format_snapshot_for_display,
    create_player_from_snapshot,
    OfflineSnapshots,
)


def list_snapshots_cmd():
    """列出所有可奪舍的快照"""
    offline = get_offline_snapshots()
    snapshots = offline.get_all_snapshots()
    
    if not snapshots:
        print("❌ 没有可用的快照")
        return
    
    print(f"📋 可奪舍的快照（{len(snapshots)}个）：\n")
    
    for i, snapshot in enumerate(snapshots, 1):
        print(f"{i}. {snapshot.label}")
        print(f"   ID: {snapshot.snapshot_id}")
        print(f"   玩家ID: {snapshot.player_id}")
        print(f"   创建时间: {snapshot.created_at}")
        print()


def show_snapshot_cmd(snapshot_id):
    """显示快照详情"""
    offline = get_offline_snapshots()
    snapshot = offline.get_snapshot(snapshot_id)
    
    if not snapshot:
        print(f"❌ 找不到快照：{snapshot_id}")
        return
    
    print(format_snapshot_for_display(snapshot))


def claim_snapshot_cmd(snapshot_id, new_name="新玩家", gender="男"):
    """奪舍快照"""
    offline = get_offline_snapshots()
    snapshot = offline.get_snapshot(snapshot_id)
    
    if not snapshot:
        print(f"❌ 找不到快照：{snapshot_id}")
        return
    
    if snapshot.is_claimed:
        print(f"❌ 快照已经被奪舍了：{snapshot.label}")
        return
    
    # 如果输入的是数字，转换为预设ID
    try:
        num = int(snapshot_id)
        snapshot_id = f"predefined_00{num}"
        snapshot = offline.get_snapshot(snapshot_id)
    except ValueError:
        pass
    
    if not snapshot:
        print(f"❌ 找不到快照：{snapshot_id}")
        return
    
    # 奪舍
    player_id = f"offline_player_{snapshot.snapshot_id}"
    success = offline.claim_snapshot(snapshot_id, player_id)
    
    if success:
        print(f"✅ 成功奪舍：{snapshot.label}")
        print(f"   你的新ID：{player_id}")
        print()
        
        # 创建 Player 对象
        player = create_player_from_snapshot(snapshot)
        print(f"✅ 角色已创建：{player.name}")
        print(f"   职业：{player.profession.value}")
        print(f"   等级：{player.level}")
        print(f"   HP：{player.hp}/{player.max_hp}")
        print(f"   金币：{player.gold}")
        print(f"   当前场景：{snapshot.game_state['current_scene_id']}")
        print()
        print("💡 你现在可以用这个角色继续游戏了！")
        print()
        print("🎮 游戏启动命令：")
        print("   python -m streamlit run frontend/app.py")
        print(f"   或双击 start.bat")
    else:
        print(f"❌ 奪舍失败")


def list_my_snapshots_cmd(player_id):
    """列出我的快照"""
    offline = get_offline_snapshots()
    snapshots = offline.list_my_snapshots(player_id)
    
    if not snapshots:
        print(f"❌ 没有奪舍的快照：{player_id}")
        return
    
    print(f"📋 我的快照（{len(snapshots)}个）：\n")
    
    for i, snapshot in enumerate(snapshots, 1):
        print(f"{i}. {snapshot.label}")
        print(f"   ID: {snapshot.snapshot_id}")
        print(f"   奪舍时间：{snapshot.claimed_at}")
        print()


def main():
    parser = argparse.ArgumentParser(description="奪舍系统命令行工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出所有可奪舍的快照')
    list_parser.set_defaults(func=lambda args: list_snapshots_cmd())
    
    # show 命令
    show_parser = subparsers.add_parser('show', help='显示快照详情')
    show_parser.add_argument('snapshot_id', help='快照ID或序号')
    show_parser.set_defaults(func=lambda args: show_snapshot_cmd(args.snapshot_id))
    
    # claim 命令
    claim_parser = subparsers.add_parser('claim', help='奪舍快照')
    claim_parser.add_argument('snapshot_id', help='快照ID或序号（1-5）')
    claim_parser.add_argument('--name', help='你的新名字（可选）', default="新玩家")
    claim_parser.add_argument('--gender', help='性别（默认：男）', default="男")
    claim_parser.set_defaults(func=lambda args: claim_snapshot_cmd(args.snapshot_id, args.name, args.gender))
    
    # my 命令
    my_parser = subparsers.add_parser('my', help='列出我的快照')
    my_parser.add_argument('player_id', help='玩家ID')
    my_parser.set_defaults(func=lambda args: list_my_snapshots_cmd(args.player_id))
    
    # 解析参数
    args = parser.parse_args()
    
    # 执行命令
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
