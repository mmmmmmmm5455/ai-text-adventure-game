# 奪舍系统 - 离线模式 🎭🌙

**版本：** 1.0  
**创建时间：** 2026年4月7日 06:35  
**状态：** ✅ 完成并测试通过

---

## 📖 文档索引

1. **[使用指南](OFFLINE_POSSESSION_GUIDE.md)** - 快速开始和命令详解
2. **[预设角色列表](PREDEFINED_SNAPSHOTS.md)** - 5个预设角色详情

---

## 🎯 系统概述

### 离线模式的特点：

- ✅ **无需数据库** - 不需要 PostgreSQL
- ✅ **即开即使用** - 无需配置，开箱即用
- ✅ **5个预设角色** - 涵盖所有职业和难度
- ✅ **完整游戏数据** - 属性、物品、任务、场景
- ✅ **丰富的背景故事** - 每个角色都有独特的故事

### 奪舍系统核心功能：

1. **列出快照** - 查看所有可奪舍的角色
2. **查看详情** - 查看角色的完整信息
3. **奪舍** - 接管角色，开始新故事
4. **我的快照** - 查看已奪舍的角色

---

## 🚀 3步快速体验

### 步骤 1：列出角色

```bash
python tools/possession_cli.py list
```

### 步骤 2：选择角色

```bash
# 查看角色详情
python tools/possession_cli.py show predefined_001
python tools/possession_cli.py show predefined_002
python tools/possession_cli.py show predefined_003
python tools/possession_cli.py show predefined_004
python tools/possession_cli.py show predefined_005
```

### 步骤 3：奪舍角色

```bash
python tools/possession_cli.py claim predefined_001 --name "你的名字" --gender "性别"
```

### 步骤 4：启动游戏

```bash
python -m streamlit run frontend/app.py
# 或双击 start.bat
```

---

## 🎭 预设角色概览

| 角色 | 职业 | 等级 | HP | MP | 章节 | 难度 | 推荐度 |
|------|------|------|-----|-----|------|------|--------|
| 铁血战士 | 战士 | 5 | 150 | - | 1 | ⭐⭐ | 新手推荐 |
| 奥术师 | 法师 | 8 | 80 | 120 | 2 | ⭐⭐⭐ | 魔法师爱好者 |
| 暗影盗贼 | 盗贼 | 6 | 100 | - | 2 | ⭐⭐⭐ | 冒险玩家 |
| 银月吟游诗人 | 吟游诗人 | 4 | 90 | 80 | 1 | ⭐⭐ | 社交玩家 |
| 废土医生 | 战士 | 7 | 130 | - | 3 | ⭐⭐⭐⭐ | 完整体验 |

---

## 💡 使用建议

### 按难度推荐：

**新手（第1次）：**
1. 铁血战士（predefined_001）
2. 银月吟游诗人（predefined_004）

**进阶（有经验）：**
1. 奥术师（predefined_002）
2. 暗影盗贼（predefined_003）

**挑战（专家）：**
1. 废土医生（predefined_005）

### 按玩法推荐：

**战斗爱好者：**
1. 铁血战士（predefined_001）
2. 废土医生（predefined_005）

**魔法爱好者：**
1. 奥术师（predefined_002）

**潜行爱好者：**
1. 暗影盗贼（predefined_003）

**社交爱好者：**
1. 银月吟游诗人（predefined_004）

**完整体验：**
1. 废土医生（predefined_005）- 3章内容丰富

---

## 🎮 技术架构

### 文件结构：

```
game/
└── possession_offline.py        # 离线奪舍核心模块

tools/
└── possession_cli.py           # 命令行工具

docs/possession/
├── OFFLINE_POSSESSION_GUIDE.md  # 使用指南
├── PREDEFINED_SNAPSHOTS.md     # 预设角色列表
├── GAME_DESIGN_DOCUMENT.md    # 设计文档
├── LLM_PROMPT_TEMPLATES.md     # LLM Prompt 模板
└── SAVE_FILE_SCHEMA.md       # 存档 Schema
```

### 核心类：

- `OfflineSnapshots` - �线快照管理器
- `SnapshotDetailDTO` - 快照详情数据类

### 主要方法：

```python
# 获取所有可奪舍的快照
snapshots = get_offline_snapshots().get_all_snapshots()

# 获取快照详情
snapshot = get_offline_snapshots().get_snapshot(snapshot_id)

# 奪舍快照
success = get_offline_snapshots().claim_snapshot(snapshot_id, player_id)

# 创建 Player 对象
player = create_player_from_snapshot(snapshot)
```

---

## 🔧 开发者指南

### 如何添加新的预设角色：

1. 编辑 `game/possession_offline.py`
2. 在 `_load_predefined_snapshots()` 方法中添加新角色数据
3. 参考现有角色的格式

### 如何扩展功能：

- 添加新的预设角色
- 添加快照编辑功能
- 添加快照分享功能
- 添加快照导入/导出

---

## 🎊 开始体验！

现在就可以在没有数据库的情况下体验奪舍系统了！

**快速开始：**
```bash
# 1. 查看角色
python tools/possession_cli.py list

# 2. 奪舍角色
python tools/possession_cli.py claim predefined_001 --name "我的名字"

# 3. 启动游戏
python -m streamlit run frontend/app.py
```

**详细指南：**
- 查看 [使用指南](OFFLINE_POSSESSION_GUIDE.md)
- 查看 [预设角色列表](PREDEFINED_SNAPSHOTS.md)

---

**设计者：** 你和我 🐉  
**版本：** 1.0  
**状态：** ✅ 可使用
