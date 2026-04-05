"""存档迁移测试。"""

from __future__ import annotations

from game.save_migrations import CURRENT_SAVE_SCHEMA, migrate_save_dict
from story.manifest import STORY_ASSET_VERSION


def test_migrate_old_save_without_schema() -> None:
    data: dict = {"player": {}, "quests": {"quests": []}}
    migrate_save_dict(data)
    assert data["schema_version"] == CURRENT_SAVE_SCHEMA
    assert data.get("story_asset_version") == STORY_ASSET_VERSION
    assert data.get("companions") == []
    assert data.get("pending_companion_offer") is None
    assert data.get("flavor_log") == []
    assert data.get("stat_counters") == {}
    assert data.get("meta_break_budget") == 3
