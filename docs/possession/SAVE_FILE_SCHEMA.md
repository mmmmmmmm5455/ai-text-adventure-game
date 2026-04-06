{
  "_meta": {
    "version": "1.0.0",
    "description": "AI 文字冒險遊戲 — 統一存檔文件 JSON Schema",
    "updated": "2026-04-06",
    "status": "草稿",
    "notes": [
      "所有客戶端/服務端交換和持久化均使用此 Schema",
      "客戶端不得假設任何未在此文檔中聲明的欄位存在",
      "枚舉值（enums）若出現未知值，應回退到安全默認值而非拋錯"
    ]
  },

  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://text-adventure.game/schemas/savefile/v1.json",

  "title": "TextAdventureSave",
  "description": "文字冒險遊戲存檔文件根結構",
  "type": "object",
  "required": ["schema_version", "save_id", "created_at", "updated_at", "player", "game"],

  "additionalProperties": true,

  "properties": {

    "--------------------------------------------------------------------------------": {
      "_comment": "========================== 元數據 =========================="
    },

    "schema_version": {
      "description": "存檔 Schema 版本。與 STORY_ASSET_VERSION 獨立。",
      "type": "integer",
      "minimum": 1,
      "examples": [5]
    },

    "save_id": {
      "description": "存檔唯一標識（UUID v4）。",
      "type": "string",
      "format": "uuid"
    },

    "save_label": {
      "description": "玩家自定義存檔名（如「廣場冒險第三章」）。",
      "type": ["string", "null"],
      "maxLength": 128
    },

    "created_at": {
      "description": "存檔創建時間（ISO 8601 / RFC 3339，含時區）。",
      "type": "string",
      "format": "date-time"
    },

    "updated_at": {
      "description": "最後修改時間（ISO 8601 / RFC 3339，含時區）。",
      "type": "string",
      "format": "date-time"
    },

    "playtime_seconds": {
      "description": "玩家總遊玩時長（秒）。",
      "type": "integer",
      "minimum": 0,
      "examples": [3600]
    },

    "story_asset_version": {
      "description": "劇情資產版本號（用於兼容性校驗）。",
      "type": "string",
      "examples": ["1.2.0"]
    },

    "--------------------------------------------------------------------------------": {
      "_comment": "========================== 遊戲狀態 =========================="
    },

    "game": {
      "description": "核心遊戲狀態（非玩家相關的全局狀態）。",
      "type": "object",
      "required": ["scene_id", "round_count", "chapter"],
      "properties": {

        "scene_id": {
          "description": "當前場景 ID。",
          "type": "string",
          "examples": ["village_square", "forest_entrance", "dimensional_rift"]
        },

        "chapter": {
          "description": "當前章節編號（影響劇情進度）。",
          "type": "integer",
          "minimum": 1,
          "examples": [3]
        },

        "round_count": {
          "description": "總行動回合數（影響時間流逝、食物消耗等）。",
          "type": "integer",
          "minimum": 0
        },

        "time_period_index": {
          "description": "時段索引：0=黎明, 1=上午, 2=下午, 3=黃昏, 4=夜晚, 5=午夜",
          "type": "integer",
          "minimum": 0,
          "maximum": 5,
          "default": 0
        },

        "world_state_modifier": {
          "description": "全局世界狀態modifier（如「豐收年」「瘟疫季」「次元潮汐」）。",
          "type": ["string", "null"],
          "examples": ["famine_year", "plague_season", "dimensional_tide", "trade_blockade"]
        },

        "rng_seed": {
          "description": "當前 RNG 隨機種子（調試/重放用）。為 null 表示使用系統隨機。",
          "type": ["integer", "null"]
        },

        "unlocked_scenes": {
          "description": "已解鎖場景 ID 列表。",
          "type": "array",
          "items": { "type": "string" },
          "uniqueItems": true,
          "default": []
        },

        "completed_quest_ids": {
          "description": "已完成任務 ID 列表。",
          "type": "array",
          "items": { "type": "string" },
          "uniqueItems": true,
          "default": []
        },

        "active_quest_ids": {
          "description": "進行中任務 ID 列表。",
          "type": "array",
          "items": { "type": "string" },
          "uniqueItems": true,
          "default": []
        },

        "world_flags": {
          "description": "任意鍵值標記（觸發特定劇情/解鎖內容）。",
          "type": "object",
          "additionalProperties": true,
          "default": {}
        },

        "narrative_achievement_ids": {
          "description": "已解鎖叙事成就 ID 列表。",
          "type": "array",
          "items": { "type": "string" },
          "default": []
        },

        "game_log": {
          "description": "遊戲日誌（最近200條，用於生成last_words等）。",
          "type": "array",
          "items": { "type": "string" },
          "maxItems": 200
        },

        "key_choices": {
          "description": "關鍵選擇記錄（影響結局判定）。",
          "type": "array",
          "items": { "type": "string" },
          "maxLength": 500,
          "default": []
        },

        "tags": {
          "description": "任意標籤集（自由標記）。",
          "type": "array",
          "items": { "type": "string", "maxLength": 64 },
          "default": []
        }
      }
    },

    "--------------------------------------------------------------------------------": {
      "_comment": "========================== 玩家 =========================="
    },

    "player": {
      "description": "玩家角色完整數據。",
      "type": "object",
      "required": ["name", "level", "hp", "max_hp", "stats", "traits"],
      "properties": {

        "id": {
          "description": "玩家實例 ID（UUID）。",
          "type": ["string", "null"]
        },

        "name": {
          "description": "角色名稱。",
          "type": "string",
          "maxLength": 32
        },

        "gender": {
          "description": "性別。",
          "type": "string",
          "default": "未指定"
        },

        "level": {
          "type": "integer",
          "minimum": 1,
          "default": 1
        },

        "xp": {
          "description": "當前經驗值。",
          "type": "integer",
          "minimum": 0,
          "default": 0
        },

        "gold": {
          "description": "金幣。",
          "type": "integer",
          "minimum": 0,
          "default": 20
        },

        "profession": {
          "description": "職業（如 WARRIOR/MAGE/ROGUE/BARD）。",
          "type": "string",
          "enum": ["WARRIOR", "MAGE", "ROGUE", "BARD", ""]
        },

        "hp": {
          "description": "當前生命值。",
          "type": "integer"
        },

        "max_hp": {
          "description": "最大生命值。",
          "type": "integer"
        },

        "mp": {
          "description": "當前魔法值。",
          "type": "integer",
          "default": 30
        },

        "max_mp": {
          "description": "最大魔法值。",
          "type": "integer",
          "default": 30
        },

        "stats": {
          "description": "6維屬性對象（SPECIAL-like）。",
          "type": "object",
          "required": ["str", "per", "end", "cha", "int", "agl"],
          "properties": {
            "str": { "type": "integer", "minimum": 1, "maximum": 99, "description": "力量" },
            "per": { "type": "integer", "minimum": 1, "maximum": 99, "description": "感知" },
            "end": { "type": "integer", "minimum": 1, "maximum": 99, "description": "體質" },
            "cha": { "type": "integer", "minimum": 1, "maximum": 99, "description": "魅力" },
            "int": { "type": "integer", "minimum": 1, "maximum": 99, "description": "智力" },
            "agl": { "type": "integer", "minimum": 1, "maximum": 99, "description": "敏捷" }
          },
          "examples": [{ "str": 4, "per": 7, "end": 5, "cha": 5, "int": 6, "agl": 3 }]
        },

        "background_id": {
          "description": "角色背景 ID（如 wasteland_doctor）。",
          "type": ["string", "null"]
        },

        "background_name": {
          "description": "角色背景顯示名（如「廢土醫生」）。",
          "type": ["string", "null"]
        },

        "traits": {
          "description": "特質 ID 列表（如 [iron_stomach, bad_sense_of_direction]）。",
          "type": "array",
          "items": { "type": "string" },
          "default": []
        },

        "inventory": {
          "$ref": "#/definitions/Inventory"
        },

        "equipped_weapon_id": {
          "description": "已裝備武器 ID。",
          "type": ["string", "null"]
        },

        "equipped_armor_id": {
          "description": "已裝備防具 ID。",
          "type": ["string", "null"]
        },

        "skills": {
          "description": "技能 ID 列表。",
          "type": "array",
          "items": { "type": "string" },
          "default": []
        },

        "is_mancelled": {
          "description": "是否為菌人狀態。",
          "type": "boolean",
          "default": false
        },

        "mold_skills": {
          "description": "菌人狀態解鎖的技能列表。",
          "type": "array",
          "items": { "type": "string" },
          "default": []
        },

        "mold_infection_rounds": {
          "description": "感染回合數（影響菌人結局判定）。",
          "type": "integer",
          "minimum": 0,
          "default": 0
        },

        "dimensional_fragments": {
          "description": "已收集的次元碎片數量（集齊5塊解鎖特殊結局）。",
          "type": "integer",
          "minimum": 0,
          "maximum": 99,
          "default": 0
        },

        "dimensional_energy": {
          "description": "次元穿梭能量（每次穿梭消耗）。",
          "type": "integer",
          "minimum": 0,
          "default": 3
        },

        "dimensional_rift_charges": {
          "description": "剩餘免費穿梭次數（當前章節）。",
          "type": "integer",
          "minimum": 0,
          "default": 2
        },

        "dimensional_rift_cooldown_rounds": {
          "description": "穿梭冷卻剩餘回合數。",
          "type": "integer",
          "minimum": 0,
          "default": 0
        },

        "current_body_id": {
          "description": "當前操控的身體 ID（默認 player_body）。",
          "type": "string",
          "default": "player_body"
        },

        "active_body_swaps": {
          "description": "曾經交換過的身體記錄（用於結局判定）。",
          "type": "array",
          "items": { "$ref": "#/definitions/BodySwapRecord" },
          "default": []
        },

        "luck_value": {
          "description": "幸運值（1~100，影響 RNG 判定偏移）。",
          "type": "integer",
          "minimum": 1,
          "maximum": 100,
          "default": 50
        },

        "meta_break_budget": {
          "description": "元突破預算（遊戲機制護城河）。",
          "type": "integer",
          "minimum": 0,
          "default": 3
        },

        "companion_loyalty_global_modifier": {
          "description": "全局隊友忠誠度修正（正/負）。",
          "type": "integer",
          "default": 0
        },

        "companion_ids": {
          "description": "當前隊友 ID 列表（與下方的 companions 數組對應）。",
          "type": "array",
          "items": { "type": "string" },
          "default": []
        }
      }
    },

    "--------------------------------------------------------------------------------": {
      "_comment": "========================== 背包 =========================="
    },

    "definitions": {

      "Inventory": {
        "description": "背包容器。",
        "type": "object",
        "properties": {
          "slots_used": { "type": "integer" },
          "max_slots": { "type": "integer" },
          "items": {
            "type": "array",
            "items": { "$ref": "#/definitions/InventoryItem" }
          }
        }
      },

      "InventoryItem": {
        "description": "背包中的單一物品。",
        "type": "object",
        "required": ["item_id", "name", "quantity"],
        "properties": {

          "item_id": {
            "description": "物品全局唯一 ID（如 rusty_sword, healing_potion）。",
            "type": "string"
          },

          "name": {
            "description": "顯示名稱。",
            "type": "string"
          },

          "category": {
            "description": "物品類別枚舉。",
            "type": "string",
            "enum": [
              "WEAPON", "ARMOR", "CONSUMABLE", "QUEST_ITEM",
              "MATERIAL", "KEY_ITEM", "DIMENTIONAL_ITEM", "COMPANION_ITEM"
            ]
          },

          "quantity": {
            "description": "數量（堆疊物品）。",
            "type": "integer",
            "minimum": 1
          },

          "current_durability": {
            "description": "當前耐久度（null 表示無耐久）。",
            "type": ["integer", "null"]
          },

          "max_durability": {
            "description": "最大耐久度。",
            "type": ["integer", "null"]
          },

          "is_equipped": {
            "description": "當前是否已裝備。",
            "type": "boolean",
            "default": false
          },

          "dimentional_origin": {
            "description": "物品來源（普通/異界/霉菌）。",
            "type": "string",
            "enum": ["normal", "dimensional", "mold"],
            "default": "normal"
          },

          "custom_properties": {
            "description": "物品自定義附加屬性（稀有詞綴等）。",
            "type": "object",
            "additionalProperties": true,
            "default": {}
          }
        }
      },

      "BodySwapRecord": {
        "description": "交換身體記錄。",
        "type": "object",
        "required": ["original_body_id", "target_body_id", "swap_round"],
        "properties": {
          "original_body_id": { "type": "string" },
          "target_body_id": { "type": "string" },
          "swap_round": { "type": "integer" },
          "reversed": { "type": "boolean", "default": false },
          "reversed_round": { "type": ["integer", "null"] }
        }
      },

      "Companion": {
        "description": "隊友實例。",
        "type": "object",
        "required": ["companion_id", "name", "personality", "special_skill", "loyalty_score"],
        "properties": {

          "companion_id": {
            "description": "隊友唯一 ID（如 c_001）。",
            "type": "string"
          },

          "name": {
            "description": "隊友名稱。",
            "type": "string"
          },

          "appearance": {
            "description": "外貌描述。",
            "type": "string"
          },

          "personality": {
            "description": "性格描述。",
            "type": "string"
          },

          "special_skill": {
            "description": "特殊技能名稱。",
            "type": "string"
          },

          "hidden_trait": {
            "description": "隱藏特質（間諜/懦夫/忠犬/野心家/詛咒者）。",
            "type": ["object", "null"],
            "properties": {
              "type": {
                "type": "string",
                "enum": ["間諜", "懦夫", "忠犬", "野心家", "詛咒者"]
              },
              "value": {
                "description": "傾向強度（0~1）。",
                "type": "number",
                "minimum": 0,
                "maximum": 1
              },
              "clue_line": {
                "description": "平時對話中可能暴露的台詞。",
                "type": "string"
              },
              "is_betrayer": {
                "description": "最終是否叛變（結局時計算）。",
                "type": "boolean",
                "default": false
              },
              "revealed": {
                "description": "是否已被揭開。",
                "type": "boolean",
                "default": false
              }
            }
          },

          "loyalty_score": {
            "description": "忠誠度（0~100）。",
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "default": 50
          },

          "join_condition": {
            "description": "入隊條件描述。",
            "type": "string"
          },

          "events_log": {
            "description": "與該隊友相關的關鍵事件（如「他救了你的命」）。",
            "type": "array",
            "items": { "type": "string" },
            "default": []
          },

          "special_ability_charges": {
            "description": "特殊技能剩餘使用次數（-1=無限）。",
            "type": "integer",
            "default": -1
          },

          "status": {
            "description": "當前狀態。",
            "type": "string",
            "enum": ["active", "temporarily_left", "dead", "betrayed", "missing"],
            "default": "active"
          }
        }
      },

      "DynamicNPC": {
        "description": "動態生成的 NPC 實例。",
        "type": "object",
        "required": ["npc_id", "name", "personality", "disposition"],
        "properties": {
          "npc_id": { "type": "string" },
          "name": { "type": "string" },
          "appearance": { "type": "string" },
          "personality": { "type": "string" },
          "disposition": {
            "description": "對玩家態度。",
            "type": "string",
            "enum": ["friendly", "neutral", "hostile", "scared", "greedy"]
          },
          "quest_id": { "type": ["string", "null"] },
          "reward_description": { "type": ["string", "null"] },
          "flavor_text": { "type": "string" },
          "is_mercenary": {
            "description": "是否為僱傭兵（可付錢直接加入）。",
            "type": "boolean",
            "default": false
          },
          "met_rounds_ago": {
            "description": "上次遇見是幾回合前（影響是否還在廣場）。",
            "type": "integer",
            "minimum": 0,
            "default": 0
          }
        }
      },

      "Quest": {
        "description": "任務實例。",
        "type": "object",
        "required": ["quest_id", "title", "status"],
        "properties": {
          "quest_id": { "type": "string" },
          "title": { "type": "string" },
          "description": { "type": "string" },
          "status": {
            "type": "string",
            "enum": ["active", "completed", "failed", "hidden"]
          },
          "giver": { "type": ["string", "null"] },
          "objectives": {
            "type": "array",
            "items": { "$ref": "#/definitions/QuestObjective" }
          },
          "rewards": {
            "type": "array",
            "items": { "type": "string" }
          },
          "chapter": { "type": "integer" },
          "is_repeatable": { "type": "boolean" }
        }
      },

      "QuestObjective": {
        "description": "任務目標。",
        "type": "object",
        "required": ["id", "description", "completed"],
        "properties": {
          "id": { "type": "string" },
          "description": { "type": "string" },
          "completed": { "type": "boolean" },
          "target_count": { "type": "integer" },
          "current_count": { "type": "integer" }
        }
      },

      "DimensionalRift": {
        "description": "次元裂縫實例。",
        "type": "object",
        "required": ["scene_name", "atmosphere", "rounds_remaining", "interactables"],
        "properties": {
          "scene_name": { "type": "string" },
          "atmosphere": { "type": "string" },
          "description": { "type": "string" },
          "rounds_remaining": {
            "description": "剩餘行動回合數。",
            "type": "integer"
          },
          "interactables": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "name": { "type": "string" },
                "desc": { "type": "string" },
                "action_type": {
                  "type": "string",
                  "enum": ["explore", "dialogue", "fight", "pick", "search"]
                },
                "completed": { "type": "boolean", "default": false },
                "reward_id": { "type": ["string", "null"] }
              }
            }
          },
          "secret_found": {
            "description": "是否已找到隱藏秘密。",
            "type": "boolean",
            "default": false
          },
          "secret_type": {
            "type": ["string", "null"],
            "enum": ["companion", "item", "clue", null]
          },
          "secret_content": { "type": ["string", "null"] }
        }
      },

      "RepairRecipe": {
        "description": "修理記錄（用於計算修理歷史）。",
        "type": "object",
        "required": ["item_id", "timestamp", "method", "durability_restored"],
        "properties": {
          "item_id": { "type": "string" },
          "timestamp": { "type": "string", "format": "date-time" },
          "method": {
            "type": "string",
            "enum": ["self", "npc", "mold", "dimensional"]
          },
          "durability_restored": { "type": "integer" },
          "material_cost": { "type": ["integer", "null"] },
          "gold_cost": { "type": ["integer", "null"] },
          "was_critical": { "type": "boolean", "default": false }
        }
      },

      "LootHistoryEntry": {
        "description": "摸尸體歷史記錄。",
        "type": "object",
        "properties": {
          "round": { "type": "integer" },
          "scene_id": { "type": "string" },
          "result_type": {
            "type": "string",
            "enum": ["gold", "item", "clue", "curse", "special", "nothing"]
          },
          "item_id": { "type": ["string", "null"] },
          "description": { "type": "string" }
        }
      }
    },

    "--------------------------------------------------------------------------------": {
      "_comment": "========================== 擴展數據 =========================="
    },

    "companions": {
      "description": "當前隊友列表。",
      "type": "array",
      "items": { "$ref": "#/definitions/Companion" },
      "default": []
    },

    "dynamic_npcs": {
      "description": "當前場景中的動態 NPC 列表。",
      "type": "array",
      "items": { "$ref": "#/definitions/DynamicNPC" },
      "default": []
    },

    "active_rift": {
      "description": "當前活躍的次元裂縫實例（null 表示不在異界）。",
      "type": ["object", "null"],
      "$ref": "#/definitions/DimensionalRift"
    },

    "repair_history": {
      "description": "修理歷史（用於成就/統計）。",
      "type": "array",
      "items": { "$ref": "#/definitions/RepairRecipe" },
      "default": []
    },

    "loot_history": {
      "description": "摸尸體歷史記錄。",
      "type": "array",
      "items": { "$ref": "#/definitions/LootHistoryEntry" },
      "maxItems": 100,
      "default": []
    },

    "npc_mood": {
      "description": "NPC 情緒地圖（npc_id → mood）。",
      "type": "object",
      "additionalProperties": {
        "type": "string",
        "enum": ["friendly", "neutral", "annoyed", "hostile", "scared", "greedy"]
      },
      "default": {}
    },

    "world_evolution": {
      "description": "世界演化歷史（如「瘟疫爆發」「商人罷工」）。",
      "type": "array",
      "items": { "type": "string" },
      "default": []
    },

    "stat_counters": {
      "description": "各類行為統計計數器。",
      "type": "object",
      "additionalProperties": { "type": "integer" },
      "examples": [{
        "enemies_killed": 15,
        "corpses_looted": 8,
        "npcs_convinced": 4,
        "companion_betrayals": 0,
        "mold_interactions": 1,
        "dimensional_rifts_entered": 3,
        "items_repaired": 6,
        "games_saved": 12
      }]
    },

    "companion_fate_log": {
      "description": "隊友結局事件日誌（用於結局敘事）。",
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "companion_id": { "type": "string" },
          "round": { "type": "integer" },
          "fate": { "type": "string" },
          "summary": { "type": "string" }
        }
      },
      "default": []
    },

    "flavor_log": {
      "description": "純敘述性趣聞日誌（不影響遊戲邏輯）。",
      "type": "array",
      "items": { "type": "object" },
      "default": []
    },

    "pending_gift_box": {
      "description": "是否存在待開啟的禮物盒。",
      "type": "boolean",
      "default": false
    },

    "newspaper_issue": {
      "description": "已發布的遊戲內報紙期號（用於元遊戲）。",
      "type": "integer",
      "minimum": 0,
      "default": 0
    },

    "quests": {
      "description": "任務系統根節點。",
      "type": "object",
      "properties": {
        "active_quests": {
          "type": "array",
          "items": { "$ref": "#/definitions/Quest" }
        },
        "completed_quest_ids": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },

    "--------------------------------------------------------------------------------": {
      "_comment": "========================== 擴展預留 =========================="
    },

    "_expansion_slots": {
      "description": "預留的擴展槽位（未來系統可自由使用，不破壞現有存檔）。",
      "type": "object",
      "additionalProperties": true,
      "default": {}
    }
  },

  "examples": [

    {
      "schema_version": 5,
      "save_id": "550e8400-e29b-41d4-a716-446655440000",
      "save_label": "廣場冒險 - 第3章",
      "created_at": "2026-04-01T10:00:00+08:00",
      "updated_at": "2026-04-06T04:30:00+08:00",
      "playtime_seconds": 10800,
      "story_asset_version": "1.2.0",

      "game": {
        "scene_id": "village_square",
        "chapter": 3,
        "round_count": 847,
        "time_period_index": 2,
        "world_state_modifier": "dimensional_tide",
        "rng_seed": 1701234567,
        "unlocked_scenes": ["forest_entrance", "cave", "town_tavern"],
        "completed_quest_ids": ["q_village_help", "q_merchant_trade"],
        "active_quest_ids": ["q_graveyard_mystery"],
        "world_flags": {
          "met_mysterious_stranger": true,
          "saved_blacksmith": false
        },
        "narrative_achievement_ids": ["first_kill", "first_betrayal"],
        "game_log": ["擊敗了哥布林王", "獲得了古堡地圖"],
        "key_choices": ["拒絕了賞金獵人的提議"],
        "tags": ["test_run", "speedrun_candidate"]
      },

      "player": {
        "id": "player_001",
        "name": "阿克",
        "gender": "男",
        "level": 7,
        "xp": 350,
        "gold": 280,
        "profession": "WARRIOR",
        "hp": 85,
        "max_hp": 120,
        "mp": 40,
        "max_mp": 55,
        "stats": {
          "str": 6,
          "per": 7,
          "end": 5,
          "cha": 5,
          "int": 6,
          "agl": 5
        },
        "background_id": "wasteland_doctor",
        "background_name": "廢土醫生",
        "traits": ["iron_stomach", "bad_sense_of_direction"],
        "inventory": {
          "slots_used": 12,
          "max_slots": 30,
          "items": [
            {
              "item_id": "rusty_sword",
              "name": "生鏽的鐵劍",
              "category": "WEAPON",
              "quantity": 1,
              "current_durability": 23,
              "max_durability": 50,
              "is_equipped": true,
              "dimentional_origin": "normal",
              "custom_properties": {}
            },
            {
              "item_id": "healing_potion",
              "name": "治療藥水",
              "category": "CONSUMABLE",
              "quantity": 3,
              "dimentional_origin": "normal",
              "custom_properties": {}
            }
          ]
        },
        "equipped_weapon_id": "rusty_sword",
        "equipped_armor_id": null,
        "skills": ["猛擊", "防禦姿態"],
        "is_mancelled": false,
        "mold_skills": [],
        "mold_infection_rounds": 0,
        "dimensional_fragments": 2,
        "dimensional_energy": 3,
        "dimensional_rift_charges": 1,
        "dimensional_rift_cooldown_rounds": 0,
        "current_body_id": "player_body",
        "active_body_swaps": [],
        "luck_value": 65,
        "meta_break_budget": 3,
        "companion_loyalty_global_modifier": 0,
        "companion_ids": ["c_001", "c_003"]
      },

      "companions": [
        {
          "companion_id": "c_001",
          "name": "流浪樂師·阿菲婭",
          "appearance": "揹著破舊魯特琴，左眼有一道傷疤",
          "personality": "表面玩世不恭，實則渴望被信任",
          "special_skill": "演奏激勵",
          "hidden_trait": {
            "type": "間諜",
            "value": 0.7,
            "clue_line": "「如果形勢不對，你可別怪我第一個跑。」",
            "is_betrayer": false,
            "revealed": false
          },
          "loyalty_score": 35,
          "join_condition": "幫她贖回被當掉的琴譜",
          "events_log": ["她替你擋下了一次偷襲"],
          "special_ability_charges": 2,
          "status": "active"
        }
      ],

      "dynamic_npcs": [
        {
          "npc_id": "dyn_042",
          "name": "愁眉苦臉的燈籠商人",
          "appearance": "一個穿著破舊長袍的老人，手裡提著一盞忽明忽暗的燈籠",
          "personality": "焦慮, 話癆",
          "disposition": "greedy",
          "quest_id": null,
          "reward_description": "如果你能幫他找回被風吹走的5個燈籠，他會給你一個古董護符",
          "flavor_text": "「哎，這該死的風！我的燈籠全吹跑了！」",
          "is_mercenary": false,
          "met_rounds_ago": 0
        }
      ],

      "active_rift": null,

      "npc_mood": {
        "npc_merchant_001": "friendly",
        "npc_guard_003": "hostile"
      },

      "repair_history": [
        {
          "item_id": "rusty_sword",
          "timestamp": "2026-04-05T15:30:00+08:00",
          "method": "self",
          "durability_restored": 15,
          "material_cost": 2,
          "gold_cost": null,
          "was_critical": false
        }
      ],

      "loot_history": [
        {
          "round": 234,
          "scene_id": "forest_entrance",
          "result_type": "item",
          "item_id": "ancient_key",
          "description": "在哥布林身上發現了一把古舊的鑰匙"
        }
      ],

      "stat_counters": {
        "enemies_killed": 15,
        "corpses_looted": 8,
        "companion_betrayals": 0,
        "mold_interactions": 0,
        "dimensional_rifts_entered": 1
      },

      "quests": {
        "active_quests": [
          {
            "quest_id": "q_graveyard_mystery",
            "title": "墓園的低語",
            "description": "村長說墓園裡有奇怪的聲音……",
            "status": "active",
            "giver": "village_elder",
            "objectives": [
              {
                "id": "obj_1",
                "description": "在墓園找到異常",
                "completed": false,
                "target_count": 1,
                "current_count": 0
              }
            ],
            "rewards": ["經驗+200", "古堡地圖碎片"],
            "chapter": 3,
            "is_repeatable": false
          }
        ],
        "completed_quest_ids": ["q_village_help", "q_merchant_trade"]
      },

      "_expansion_slots": {}
    }
  ]
}
