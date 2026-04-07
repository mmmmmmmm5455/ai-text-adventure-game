# 奪舍系统 - 预设角色快照（离线模式）

当无法连接 PostgreSQL 数据库时，使用这些预设角色快照进行奪舍体验。

## 🎭 预设角色列表

### 1. 铁血战士

```json
{
  "snapshot_id": "predefined_001",
  "player_id": "npc_001",
  "label": "铁血战士 - 廢土医生",
  "character": {
    "name": "铁血战士",
    "profession": "warrior",
    "gender": "男",
    "level": 5,
    "hp": 150,
    "max_hp": 150,
    "gold": 50,
    "stats": {
      "strength": 8,
      "perception": 6,
      "endurance": 7,
      "charisma": 4,
      "intelligence": 3,
      "agility": 5
    },
    "background": "wasteland_doctor",
    "traits": ["first_aid_master", "calm_minded"],
    "last_words": "我会在废土上守护每一个人。",
    "recent_events": [
      {"event": "在村庄广场治疗了受伤的守卫"},
      {"event": "从废墟中救出了一家人"},
      {"event": "学会了基本的急救技能"}
    ],
    "playtime_minutes": 120,
    "game_chapter": 1
  },
  "game_state": {
    "current_scene_id": "village_square",
    "unlocked_scenes": ["village_square", "misty_forest", "mountain_foot"],
    "active_quest_ids": ["quest_heal_wounded", "quest_find_medicine"],
    "inventory": [
      {"id": "sword_iron", "name": "铁剑", "durability": 45},
      {"id": "armor_leather", "name": "皮甲", "durability": 60}
    ]
  }
}
```

**特点：**
- 高血量和耐力
- 擁血医生背景
- 拥有治疗技能
- 已解锁3个场景
- 进行中，1章

---

### 2. 艾术师

```json
{
  "snapshot_id": "predefined_002",
  "player_id": "npc_002",
  "label": "奥术师 - 流浪学者",
  "character": {
    "name": "奥术师",
    "profession": "mage",
    "gender": "女",
    "level": 8,
    "hp": 80,
    "max_hp": 80,
    "mp": 120,
    "max_mp": 120,
    "gold": 100,
    "stats": {
      "strength": 3,
      "perception": 5,
      "endurance": 4,
      "charisma": 6,
      "intelligence": 10,
      "agility": 4
    },
    "background": "drifter",
    "traits": ["social_butterfly", "keen_eye"],
    "last_words": "魔法不是为了毁灭，而是为了保护。",
    "recent_events": [
      {"event": "在迷雾森林中发现了古代遗迹"},
      {"event": "学会了新的奥术法术"},
      {"event": "结交了一位神秘的商人"}
    ],
    "playtime_minutes": 180,
    "game_chapter": 2
  },
  "game_state": {
    "current_scene_id": "misty_forest",
    "unlocked_scenes": ["village_square", "misty_forest", "ancient_ruins", "mountain_foot"],
    "active_quest_ids": ["quest_find_relic", "quest_learn_spell"],
    "inventory": [
      {"id": "staff_apprentice", "name": "学徒法杖", "durability": 70},
      {"id": "potion_mana", "name": "法力药水", "quantity": 5}
    ]
  }
}
```

**特点：**
- 高智力和魔法力
- 社交花蝴蝶特质
- 发现了古代遗迹
- 探索深入，2章
- 拥有魔法物品

---

### 3. 暗影盗贼

```json
{
  "snapshot_id": "predefined_003",
  "player_id": "npc_003",
  "label": "暗影盗贼 - 拾荒者",
  "character": {
    "name": "暗影",
    "profession": "rogue",
    "gender": "男",
    "level": 6,
    "hp": 100,
    "max_hp": 100,
    "gold": 200,
    "stats": {
      "strength": 5,
      "perception": 10,
      "endurance": 6,
      "charisma": 3,
      "intelligence": 4,
      "agility": 9
    },
    "background": "scavenger",
    "traits": ["keen_eye", "night_blindness"],
    "last_words": "在黑暗中，我会是你的眼睛。",
    "recent_events": [
      {"event": "从山脚旅店偷取了重要文件"},
      {"event": "在山脚地带发现了秘密通道"},
      {"event": "被追捕，成功逃脱"}
    ],
    "playtime_minutes": 150,
    "game_chapter": 2
  },
  "game_state": {
    "current_scene_id": "mountain_foot",
    "unlocked_scenes": ["village_square", "mountain_foot", "tavern", "hidden_cave"],
    "active_quest_ids": ["quest_steal_document", "quest_escape_pursuit"],
    "inventory": [
      {"id": "dagger_shadow", "name": "暗影匕首", "durability": 55},
      {"id": "cloak_stealth", "name": "潜行斗篷", "durability": 50},
      {"id": "document_stolen", "name": "偷来的文件", "quantity": 1}
    ]
  }
}
```

**特点：**
- 高敏捷和感知
- 拥有偷窃技能
- 夜盲特质（弱点）
- 进行中，2章
- 高价值物品

---

### 4. 银月吟游诗人

```json
{
  "snapshot_id": "predefined_004",
  "player_id": "npc_004",
  "label": "银月吟游诗人 - 流浪者",
  "character": {
    "name": "银月",
    "profession": "bard",
    "gender": "女",
    "level": 4,
    "hp": 90,
    "max_hp": 90,
    "mp": 80,
    "max_mp": 80,
    "gold": 30,
    "stats": {
      "strength": 4,
      "perception": 6,
      "endurance": 5,
      "charisma": 10,
      "intelligence": 7,
      "agility": 6
    },
    "background": "drifter",
    "traits": ["social_butterfly", "calm_minded"],
    "last_words": "音乐是心灵的桥梁。",
    "recent_events": [
      {"event": "在旅店演奏获得了赞赏"},
      {"event": "记录了村庄的民谣"},
      {"event": "治愈了一个孤独的孩子"}
    ],
    "playtime_minutes": 90,
    "game_chapter": 1
  },
  "game_state": {
    "current_scene_id": "tavern",
    "unlocked_scenes": ["village_square", "tavern", "mountain_foot"],
    "active_quest_ids": ["quest_collect_stories", "quest_perform_in_tavern"],
    "inventory": [
      {"id": "lute_silver", "name": "银月琴", "durability": 80},
      {"id": "songbook", "name": "歌本", "quantity": 1}
    ]
  }
}
```

**特点：**
- 高魅力和智力
- 社交能力强
- 拥有音乐技能
- 进行早期，1章
- 社交类角色

---

### 5. 废土医生

```json
{
  "snapshot_id": "predefined_005",
  "player_id": "npc_005",
  "label": "废土医生 - 医疗专家",
  "character": {
    "name": "艾瑞亚",
    "profession": "warrior",
    "gender": "女",
    "level": 7,
    "hp": 130,
    "max_hp": 130,
    "gold": 75,
    "stats": {
      "strength": 5,
      "perception": 7,
      "endurance": 6,
      "charisma": 7,
      "intelligence": 8,
      "agility": 5
    },
    "background": "wasteland_doctor",
    "traits": ["first_aid_master", "calm_minded", "iron_stomach"],
    "positive_traits": ["first_aid_master", "calm_minded", "iron_stomach"],
    "negative_traits": [],
    "last_words": "即使世界崩塌，我也不会放弃任何一个生命。",
    "recent_events": [
      {"event": "救治了10个村庄居民"},
      {"event": "建立了临时医疗站"},
      {"event": "研制出了新的药物"}
    ],
    "playtime_minutes": 200,
    "game_chapter": 3
  },
  "game_state": {
    "current_scene_id": "village_square",
    "unlocked_scapes": ["village_square", "misty_forest", "mountain_foot", "tavern", "clinic"],
    "active_quest_ids": ["quest_cure_plague", "quest_establish_clinic"],
    "inventory": [
      {"id": "medical_kit", "name": "医疗包", "quantity": 3},
      {"id": "medicine_plague", "name": "瘟疫解药", "quantity": 1},
      {"id": "sword_doctor", "name": "医生之剑", "durability": 50}
    ]
  }
}
```

**特点：**
- 平衡型角色
- 3个正面特质
- 高等级（7级）
- 进行深入，3章
- 拥有稀有药物

---

## 🎭 使用这些预设角色

### 方法 1：在游戏中奪舍

```
1. 开始新游戏
2. 选择"奪舍"功能
3. 从预设列表中选择一个角色
4. 继续游戏，体验不同的角色
```

### 方法 2：通过代码直接加载

```python
from game.possession.offline_snapshots import OfflineSnapshots

# 加载预设快照
snapshots = OfflineSnapshots.get_all_snapshots()
snapshot = snapshots[0]  # 铁血战士

# 恢复角色
from game.game_state import GameState
state = GameState()
state.load_from_snapshot(snapshot['character'], snapshot['game_state'])
```

### 方法 3：作为测试用例

```python
# 测试不同职业的平衡性
test_snapshots = [
    load_snapshot('predefined_001'),  # 战士
    load_snapshot('predefined_002'),  # 法师
    load_snapshot('predefined_003'),  # 盗贼
    load_snapshot('predefined_004'),  # 吟游诗人
]
```

---

## 🌟 角色特色对比

| 角色 | 职业 | 等级 | HP | 特长 | 章节 |
|------|------|------|-----|------|------|
| 铁血战士 | 战士 | 5 | 150 | 高血量、耐力 | 1章 |
| 奥术师 | 法师 | 8 | 80 | 高智力、魔法 | 2章 |
| 暗影盗贼 | 盗贼 | 6 | 100 | 高敏捷、感知 | 2章 |
| 银月吟游诗人 | 吟游诗人 | 4 | 90 | 高魅力、社交 | 1章 |
| 废土医生 | 战士 | 7 | 130 | 平衡型、治疗 | 3章 |

---

## 💡 设计理念

这些预设角色涵盖了：
- ✅ 所有4个职业（战士、法师、盗贼、吟游诗人）
- ✅ 不同等级（4-8级）
- ✅ 不同游戏阶段（1-3章）
- ✅ 不同玩法风格（战斗、魔法、潜行、社交）
- ✅ 正面和负面特质的组合
- ✅ 丰富的游戏历史和背景故事

---

## 🔧 如何添加新的预设角色

按照这个格式添加新的角色快照：

```json
{
  "snapshot_id": "predefined_006",
  "player_id": "npc_006",
  "label": "角色名 - 背景描述",
  "character": {
    "name": "角色名",
    "profession": "warrior/mage/rogue/bard",
    "gender": "男/女",
    "level": 1-10,
    "hp": 1-200,
    "max_hp": 1-200,
    "mp": 1-200,
    "max_mp": 1-200,
    "gold": 0-1000,
    "stats": {
      "strength": 1-10,
      "perception": 1-10,
      "endurance": 1-10,
      "charisma": 1-10,
      "intelligence": 1-10,
      "agility": 1-10
    },
    "background": "wasteland_doctor/scavenger/drifter",
    "traits": ["特质1", "特质2"],
    "last_words": "最后的遗言",
    "recent_events": [
      {"event": "事件1"},
      {"event": "事件2"}
    ],
    "playtime_minutes": 0-500,
    "game_chapter": 1-5
  },
  "game_state": {
    "current_scene_id": "场景ID",
    "unlocked_scenes": ["场景1", "场景2"],
    "active_quest_ids": ["任务1", "任务2"],
    "inventory": [
      {"id": "物品ID", "name": "物品名", "durability": 0-100}
    ]
  }
}
```

---

## 🎮 奪舍体验流程

1. **选择角色** → 从5个预设角色中选择
2. **查看信息** → 阅读角色背景、属性、历史
3. **奪舍** → 接管角色，继续游戏
4. **体验不同玩法** → 感受不同职业和视角
5. **完成原剧情** → 或开启新的故事

---

## 🎊 开始奪舍之旅！

即使没有数据库，你也可以体验奪舍系统的乐趣！这些预设角色提供了：
- 🎭 不同的职业和玩法
- 📜 丰富的背景故事
- 🎯 不同的游戏进度
- 💡 创新的角色扮演体验

选择一个角色，开始你的奪舍之旅吧！🐉
