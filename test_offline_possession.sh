#!/bin/bash
# 离线奪舍系统测试脚本

echo "🎭 离线奪舍系统测试脚本"
echo "=================================="
echo ""

# 进入游戏目录
cd /workspace/projects/workspace/projects/text-adventure-game

echo "📝 测试 1：列出所有快照"
echo "----------------------------------------"
python tools/possess_cli.py list
echo ""

echo "📝 测试 2：显示快照详情（铁血战士）"
echo "----------------------------------------"
python tools/possess_cli.py show predefined_001
echo ""

echo "📝 测试 3：奪舍快照（铁血战士）"
echo "----------------------------------------"
python tools/possess_cli.py claim predefined_001 --name "测试玩家" --gender "女"
echo ""

echo "📝 测试 4：列出我的快照"
echo "----------------------------------------"
python tools/possess_cli.py my offline_player_predefined_001
echo ""

echo "📝 测试 5：显示奪舍后的快照"
echo "----------------------------------------"
python tools/possess_cli.py show predefined_001
echo ""

echo "🎭 测试完成！"
echo ""
echo "💡 提示："
echo "   - 如果所有测试都通过，说明离线奪舍系统工作正常"
echo "   - 现在你可以选择喜欢的角色奪舍，开始新的冒险！"
