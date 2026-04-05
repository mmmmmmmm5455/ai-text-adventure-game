"""游戏常量定义。"""

from __future__ import annotations

# 背包最大格子数
MAX_INVENTORY_SLOTS: int = 20

# 时间段：每经过多少回合切换一次（循环：早→中→晚→夜）
ROUNDS_PER_TIME_PERIOD: int = 5

# 时间片顺序
TIME_ORDER: tuple[str, ...] = ("早晨", "正午", "黄昏", "深夜")

# 职业枚举名（与 player 模块一致）
PROFESSION_KEYS: tuple[str, ...] = ("战士", "法师", "盗贼", "吟游诗人")
