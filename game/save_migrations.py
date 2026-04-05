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
CURRENT_SAVE_SCHEMA: int = 1


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

    # 未来示例：if v == 1 and CURRENT_SAVE_SCHEMA >= 2: _migrate_v1_to_v2(data); v = 2

    if v < CURRENT_SAVE_SCHEMA:
        data["schema_version"] = CURRENT_SAVE_SCHEMA

    data.setdefault("story_asset_version", STORY_ASSET_VERSION)
    return data
