"""
离线奪舍系统 - 当无法连接 PostgreSQL 数据库时使用
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path
from game.player import Player, Profession


@dataclass
class SnapshotDetailDTO:
    """角色快照详情"""
    snapshot_id: str
    player_id: str
    label: str
    character: dict
    game_state: dict
    created_at: str
    claimed_at: Optional[str] = None
    is_claimed: bool = False
    
    def to_dict(self) -> dict:
        return asdict(self)


class OfflineSnapshots:
    """离线奪舍快照管理器"""
    
    def __init__(self):
        self.snapshots: Dict[str, SnapshotDetailDTO] = {}
        self._load_predefined_snapshots()
    
    def _load_predefined_snapshots(self):
        """加载预设快照"""
        predefined_snapshots = {
            "predefined_001": {
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
                },
                "created_at": "2024-01-15T10:00:00Z",
                "is_claimed": False
            },
            "predefined_002": {
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
                },
                "created_at": "2024-02-20T14:30:00Z",
                "is_claimed": False
            },
            "predefined_003": {
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
                },
                "created_at": "2024-03-10T09:15:00Z",
                "is_claimed": False
            },
            "predefined_004": {
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
                },
                "created_at": "2024-01-25T16:45:00Z",
                "is_claimed": False
            },
            "predefined_005": {
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
                    "unlocked_scenes": ["village_square", "misty_forest", "mountain_foot", "tavern", "clinic"],
                    "active_quest_ids": ["quest_cure_plague", "quest_establish_clinic"],
                    "inventory": [
                        {"id": "medical_kit", "name": "医疗包", "quantity": 3},
                        {"id": "medicine_plague", "name": "瘟疫解药", "quantity": 1},
                        {"id": "sword_doctor", "name": "医生之剑", "duration": 50}
                    ]
                },
                "created_at": "2024-04-05T12:00:00Z",
                "is_claimed": False
            }
        }
        
        # 转换为 DTO 对象
        for snapshot_id, data in predefined_snapshots.items():
            self.snapshots[snapshot_id] = SnapshotDetailDTO(**data)
    
    def get_all_snapshots(self) -> List[SnapshotDetailDTO]:
        """获取所有可奪舍的快照"""
        return [s for s in self.snapshots.values() if not s.is_claimed]
    
    def get_snapshot(self, snapshot_id: str) -> Optional[SnapshotDetailDTO]:
        """获取快照详情"""
        return self.snapshots.get(snapshot_id)
    
    def claim_snapshot(self, snapshot_id: str, new_player_id: str) -> bool:
        """奪舍快照"""
        snapshot = self.snapshots.get(snapshot_id)
        if not snapshot:
            return False
        if snapshot.is_claimed:
            return False
        snapshot.is_claimed = True
        snapshot.player_id = new_player_id
        snapshot.claimed_at = "2024-04-07T06:30:00Z"
        return True
    
    def add_snapshot(self, snapshot: SnapshotDetailDTO) -> str:
        """添加新的快照"""
        self.snapshots[snapshot.snapshot_id] = snapshot
        return snapshot.snapshot_id
    
    def list_my_snapshots(self, player_id: str) -> List[SnapshotDetailDTO]:
        """列出我的快照"""
        return [s for s in self.snapshots.values() if s.player_id == player_id]
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """删除快照"""
        if snapshot_id in self.snapshots:
            del self.snapshots[snapshot_id]
            return True
        return False


# 全局实例
_offline_snapshots = OfflineSnapshots()


def get_offline_snapshots() -> OfflineSnapshots:
    """获取离线快照实例"""
    return _offline_snapshots


def create_player_from_snapshot(snapshot: SnapshotDetailDTO) -> Player:
    """从快照创建 Player 对象"""
    char_data = snapshot.character
    
    # 创建 Player 对象
    player = Player(
        name=char_data["name"],
        profession=Profession[char_data["profession"].upper()],
        gender=char_data["gender"]
    )
    
    # 设置属性
    player.level = char_data["level"]
    player.hp = char_data["hp"]
    player.max_hp = char_data["max_hp"]
    if "mp" in char_data:
        player.mp = char_data["mp"]
        player.max_mp = char_data["max_mp"]
    player.gold = char_data.get("gold", 0)
    
    # 设置状态
    player.strength = char_data["stats"]["strength"]
    player.intelligence = char_data["stats"]["intelligence"]
    player.agility = char_data["stats"]["agility"]
    player.charisma = char_data["stats"]["charisma"]
    player.perception = char_data["stats"]["perception"]
    player.endurance = char_data["stats"]["endurance"]
    
    # 设置特质（如果 Player 支持）
    if hasattr(player, 'traits'):
        player.traits = set(char_data.get("traits", []))
    
    return player


def format_snapshot_for_display(snapshot: SnapshotDetailDTO) -> str:
    """格式化快照用于显示"""
    char = snapshot.character
    
    output = []
    output.append("=" * 50)
    output.append(f"🎭 {snapshot.label}")
    output.append("=" * 50)
    output.append(f"等级：{char['level']} | 职业：{char['profession']}")
    output.append(f"HP：{char['hp']}/{char['max_hp']}")
    if 'mp' in char:
        output.append(f"MP：{char['mp']}/{char['max_mp']}")
    output.append(f"金币：{char['gold']}")
    output.append("")
    output.append("属性：")
    for stat_name, stat_value in char['stats'].items():
        stat_names = {
            'strength': '力量',
            'perception': '感知',
            'endurance': '耐力',
            'charisma': '魅力',
            'intelligence': '智力',
            'agility': '敏捷'
        }
        output.append(f"  {stat_names[stat_name]}：{stat_value}")
    output.append("")
    output.append("特质：")
    for trait in char.get('traits', []):
        output.append(f"  - {trait}")
    output.append("")
    output.append("最后遗言：")
    output.append(f"  \"{char['last_words']}\"")
    output.append("")
    output.append("最近事件：")
    for event in char.get('recent_events', []):
        output.append(f"  • {event['event']}")
    output.append("")
    output.append(f"游戏进度：第{char['game_chapter']}章 | 游玩时间：{char['playtime_minutes']}分钟")
    output.append("")
    output.append("当前任务：")
    for quest in snapshot.game_state.get('active_quest_ids', []):
        output.append(f"  - {quest}")
    output.append("")
    output.append("装备物品：")
    for item in snapshot.game_state.get('inventory', []):
        if 'durability' in item:
            output.append(f"  - {item['name']} (耐久度：{item['durability']})")
        elif 'quantity' in item:
            output.append(f"  - {item['name']} (数量：{item['quantity']})")
        else:
            output.append(f"  - {item['name']}")
    output.append("=" * 50)
    
    return "\n".join(output)


# 示例用法
if __name__ == "__main__":
    from core.config import get_settings
    from database.possession_db import possession_backend_ready
    
    print("🎭 离线奪舍系统测试")
    print("=" * 50)
    
    # 检查数据库是否可用
    if possession_backend_ready():
        print("✅ PostgreSQL 数据库可用")
        print("   使用数据库模式")
    else:
        print("⚠️  PostgreSQL 数据库不可用")
        print("   使用离线模式")
    
    # 获取离线快照
    offline = get_offline_snapshots()
    snapshots = offline.get_all_snapshots()
    
    print(f"\n📋 可奪舍的快照（{len(snapshots)}个）：")
    print()
    
    for i, snapshot in enumerate(snapshots, 1):
        print(f"{i}. {snapshot.label}")
        print(format_snapshot_for_display(snapshot))
        print()
    
    # 测试奪舍
    if snapshots:
        print("🎯 测试奪舍第一个快照")
        print("-" * 50)
        snapshot = snapshots[0]
        
        claimed = offline.claim_snapshot(
            snapshot.snapshot_id,
            "test_player_001"
        )
        
        if claimed:
            print(f"✅ 成功奪舍：{snapshot.label}")
        else:
            print(f"❌ 奪舍失败")
