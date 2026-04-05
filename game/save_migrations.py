"""
存档 JSON 的 schema 迁移：在反序列化为 GameState 之前对 dict 做版本升级。

原则（务实、可测试）：
- 仅处理「缺字段 / 旧版本号」；不在这里调用 LLM 或 IO。
- 每增加一个不兼容或需填充的变更，递增 CURRENT_SAVE_SCHEMA 并实现对应迁移步骤。
"""

from __future__ import annotations

from typing import Any

from story.manifest import STORY_ASSET_VERSION

# 存档文件中的 schema_version 整数；与剧情资产 STORY_ASSET_VERSION 独立
CURRENT_SAVE_SCHEMA: int = 4


def migrate_save_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    将磁盘上的存档 dict 迁移到当前 CURRENT_SAVE_SCHEMA。
    """
    v = int(data.get("schema_version", 0))
    if v == 0:
        # 无 schema_version 的旧存档：补齐元数据
        data["schema_version"] = 1
        data.setdefault("story_asset_version", STORY_ASSET_VERSION)
        v = 1

    if v < 2:
        data.setdefault("dynamic_npcs", [])
        data.setdefault("active_dynamic_npc_id", None)
        data["schema_version"] = 2
        v = 2

    if v < 3:
        data.setdefault("companions", [])
        data.setdefault("pending_companion_offer", None)
        data.setdefault("companion_fate_log", [])
        data["schema_version"] = 3
        v = 3

    if v < 4:
        data.setdefault("flavor_log", [])
        data.setdefault("world_flags", {})
        data.setdefault("world_evolution", [])
        data.setdefault("stat_counters", {})
        data.setdefault("pending_gift_box", False)
        data.setdefault("meta_break_budget", 3)
        data.setdefault("narrative_achievement_ids", [])
        data.setdefault("newspaper_issue", 0)
        data["schema_version"] = 4
        v = 4

    if v < CURRENT_SAVE_SCHEMA:
        data["schema_version"] = CURRENT_SAVE_SCHEMA

    data.setdefault("story_asset_version", STORY_ASSET_VERSION)
    return data
