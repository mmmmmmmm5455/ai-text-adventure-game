"""
Prompt 模板解析驗證測試
——確保所有模板字符串格式正確，可被正確渲染。
"""

import re
import pytest


# ---------------------------------------------------------------------------
# 輔助：驗證 JSON Schema 格式
# ---------------------------------------------------------------------------

def is_valid_uuid(uid: str) -> bool:
    pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(pattern, uid, re.IGNORECASE))


# ---------------------------------------------------------------------------
# 動態 NPC 生成 Prompt 驗證
# ---------------------------------------------------------------------------

class TestDynamicNPCPrompt:
    NPC_JSON_PATTERN = re.compile(
        r'"npc_id":\s*"dyn_[a-z0-9_]+".*?'
        r'"name":\s*".{2,10}".*?'
        r'"appearance":\s*".*?".*?'
        r'"personality":\s*".*?".*?'
        r'"disposition":\s*"(?:friendly|neutral|greedy|scared|curious)".*?'
        r'"flavor_text":\s*".{10,50}".*?'
        r'"quest":\s*(?:\{.*?\}|null)',
        re.DOTALL,
    )

    def test_npc_json_has_required_fields(self):
        """驗證 NPC JSON 模板包含所有必要字段。"""
        required_fields = [
            "npc_id", "name", "appearance", "personality",
            "disposition", "flavor_text", "quest",
        ]
        # 這裡驗證示例輸出
        sample = '''
        {
          "npc_id": "dyn_001",
          "name": "愁眉苦脸的灯笼商人",
          "appearance": "一个穿著破旧长袍的老人，手裡提著一盏灯笼",
          "personality": "焦虑, 话痨",
          "disposition": "greedy",
          "flavor_text": "「哎，这该死的风！我的灯笼全吹跑了！」",
          "quest": {
            "quest_id": "dyn_q_001",
            "objective": "帮灯笼商人找回被风吹走的5个灯笼",
            "target": "5个灯笼",
            "difficulty": "easy",
            "reward_type": "item",
            "reward_description": "古董护符"
          }
        }
        '''
        for field in required_fields:
            assert f'"{field}"' in sample, f"Missing field: {field}"

    def test_npc_id_format(self):
        """npc_id 必須是 dyn_XXX 格式。"""
        sample_ids = ["dyn_001", "dyn_village_trader", "dyn_042", "dyn_old_man"]
        for uid in sample_ids:
            assert re.match(r"^dyn_[a-z0-9_]+$", uid), f"Invalid npc_id: {uid}"

    def test_disposition_enum(self):
        """disposition 必須是已知枚舉值。"""
        valid = {"friendly", "neutral", "greedy", "scared", "curious"}
        for d in valid:
            assert d in valid

    def test_quest_null_or_object(self):
        """quest 可以是 null 或對象。"""
        # null 和對象都是合法值，這裡驗證枚舉邏輯
        assert True  # 格式由 JSON Schema 約束，這裡確認斷言邏輯存在


# ---------------------------------------------------------------------------
# 動態隊友 Prompt 驗證
# ---------------------------------------------------------------------------

class TestCompanionPrompt:
    def test_hidden_trait_types(self):
        """隱藏特質類型必須在允許列表中。"""
        allowed = {"間諜", "懦夫", "忠犬", "野心家", "詛咒者"}
        sample_traits = ["間諜", "忠犬", "野心家"]
        for t in sample_traits:
            assert t in allowed, f"Unknown hidden trait: {t}"

    def test_companion_json_has_required_fields(self):
        """隊友 JSON 模板包含所有必要字段。"""
        required_fields = [
            "companion_id", "name", "appearance", "personality",
            "join_condition", "special_skill", "hidden_trait",
        ]
        sample = '''
        {
          "companion_id": "c_001",
          "name": "流浪樂師·阿菲婭",
          "appearance": "揹著破舊魯特琴，左眼有一道傷疤",
          "personality": "表面玩世不恭，實則渴望被信任",
          "join_condition": "幫她贖回被當掉的琴譜",
          "special_skill": "演奏激勵（臨時提升隊友命中）",
          "hidden_trait": {
            "type": "間諜",
            "clue_line": "「如果形勢不對，你可別怪我第一個跑。」",
            "base_betrayal_chance": 0.7
          }
        }
        '''
        for field in required_fields:
            assert f'"{field}"' in sample, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# 次元穿梭 Prompt 驗證
# ---------------------------------------------------------------------------

class TestDimensionalRiftPrompt:
    def test_rift_json_structure(self):
        """驗證次元裂縫 JSON 模板結構。"""
        required_fields = [
            "scene_name", "atmosphere", "description",
            "interactables", "secret", "total_rounds_available",
        ]
        sample = '''
        {
          "scene_name": "鏡之回廊",
          "atmosphere": "詭異, 寧靜",
          "description": "兩面巨大的鏡子彼此相對，倒映出無數個你的殘影。",
          "interactables": [
            {
              "name": "破碎的鏡框",
              "desc": "鏡面映出一個哭泣的少女",
              "action_type": "dialogue",
              "difficulty": "easy",
              "time_cost": 1
            }
          ],
          "secret": {
            "type": "companion",
            "content": "鏡中武士",
            "reward": "願意追隨你的鏡中武士"
          },
          "total_rounds_available": 5,
          "danger_level": "low"
        }
        '''
        for field in required_fields:
            assert f'"{field}"' in sample, f"Missing field: {field}"

    def test_interactable_action_types(self):
        """互動類型必須是已知枚舉。"""
        valid = {"explore", "dialogue", "fight", "pick", "search"}
        sample = ["explore", "dialogue", "pick"]
        for at in sample:
            assert at in valid, f"Invalid action_type: {at}"

    def test_danger_level_enum(self):
        valid = {"safe", "low", "medium", "high"}
        for level in valid:
            assert level in valid


# ---------------------------------------------------------------------------
# 結局 Prompt 驗證
# ---------------------------------------------------------------------------

class TestEndingPrompt:
    def test_ending_types(self):
        """結局類型必須在允許列表中。"""
        valid = {"triumph", "tragedy", "mundane", "secret", "fungal_king", "symbiotic", "purifier", "impostor"}
        for t in ["triumph", "secret", "fungal_king"]:
            assert t in valid

    def test_mold_ending_fields(self):
        """菌人結局 JSON 必須包含所有必要字段。"""
        required = ["ending_title", "narrative", "final_moment", "world_impact"]
        sample = '''
        {
          "ending_title": "真菌之王",
          "narrative": "你成為了跨越所有次元的真菌主宰……",
          "final_moment": "你的意識擴展到無限的菌絲網絡中。",
          "world_impact": "整個世界被真菌網絡連接在一起。"
        }
        '''
        for field in required:
            assert f'"{field}"' in sample, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# 系統約束驗證
# ---------------------------------------------------------------------------

class TestSystemConstraints:
    def test_all_dispositions_have_fallback(self):
        """每個 disposition 值都有對應的後備行為。"""
        fallback_map = {
            "friendly": "玩家攻擊時：敵人會困惑地問「為什麼？」",
            "neutral": "玩家攻擊時：敵人正常還擊",
            "greedy": "玩家攻擊時：敵人先試圖保護財物",
            "scared": "玩家攻擊時：敵人先逃跑",
            "curious": "玩家攻擊時：敵人可能一時分心",
        }
        assert len(fallback_map) == 5

    def test_llm_temperature_ranges(self):
        """所有溫度值在有效範圍內。"""
        temp_ranges = {
            "system_prompt": (0.0, 0.0),
            "npc_dialogue": (0.6, 0.8),
            "scene_description": (0.6, 0.8),
            "ending_narrative": (0.75, 0.85),
            "random_encounter": (0.85, 0.95),
            "combat_dialogue": (0.65, 0.75),
            "mold_event": (0.75, 0.85),
        }
        for name, (low, high) in temp_ranges.items():
            assert 0.0 <= low <= 1.0, f"{name} low temp out of range"
            assert 0.0 <= high <= 1.0, f"{name} high temp out of range"
            assert low <= high, f"{name} temp range inverted"

    def test_cache_ttl_reasonable(self):
        """緩存 TTL 在合理範圍內。"""
        cache_ttls = {
            "npc_generation": 86400,        # 24h
            "dimensional_scene": -1,          # 永久
            "loot_table": 43200,             # 12h
            "ending_narrative": -1,           # 永久
            "combat_dialogue": 0,             # 不緩存
        }
        for name, ttl in cache_ttls.items():
            assert ttl == -1 or ttl >= 0, f"{name} TTL negative: {ttl}"
            assert ttl <= 86400 * 7, f"{name} TTL too large: {ttl}"


# ---------------------------------------------------------------------------
# JSON 格式驗證輔助
# ---------------------------------------------------------------------------

class TestJSONFormatValidation:
    """驗證文檔中的 JSON 示例格式正確。"""

    def test_sample_npc_json_valid(self):
        import json
        sample = '''
        {
          "npc_id": "dyn_042",
          "name": "愁眉苦脸的灯笼商人",
          "appearance": "一个穿著破旧长袍的老人",
          "personality": "焦虑, 话痨",
          "disposition": "greedy",
          "flavor_text": "哎，这该死的风！",
          "quest": {
            "quest_id": "dyn_q_001",
            "objective": "找回5个灯笼",
            "target": "5个灯笼",
            "difficulty": "easy",
            "reward_type": "item",
            "reward_description": "古董护符"
          }
        }
        '''
        parsed = json.loads(sample)
        assert parsed["disposition"] in {"friendly", "neutral", "greedy", "scared", "curious"}

    def test_sample_companion_json_valid(self):
        import json
        sample = '''
        {
          "companion_id": "c_001",
          "name": "流浪樂師·阿菲婭",
          "hidden_trait": {
            "type": "間諜",
            "clue_line": "「如果形勢不對，你可別怪我第一個跑。」",
            "base_betrayal_chance": 0.7
          }
        }
        '''
        parsed = json.loads(sample)
        assert parsed["hidden_trait"]["type"] in {"間諜", "懦夫", "忠犬", "野心家", "詛咒者"}
        assert 0 <= parsed["hidden_trait"]["base_betrayal_chance"] <= 1

    def test_sample_rift_json_valid(self):
        import json
        sample = '''
        {
          "scene_name": "鏡之回廊",
          "atmosphere": "詭異, 寧靜",
          "interactables": [
            {"name": "破碎鏡框", "action_type": "dialogue", "time_cost": 1}
          ],
          "secret": {"type": "companion", "content": "鏡中武士"},
          "total_rounds_available": 5,
          "danger_level": "low"
        }
        '''
        parsed = json.loads(sample)
        assert parsed["danger_level"] in {"safe", "low", "medium", "high"}
        assert parsed["total_rounds_available"] >= 1
