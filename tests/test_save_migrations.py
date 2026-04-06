"""存档迁移测试。"""

from __future__ import annotations

from game.save_migrations import CURRENT_SAVE_SCHEMA, migrate_save_dict
from story.manifest import STORY_ASSET_VERSION


def test_migrate_old_save_without_schema() -> None:
    data: dict = {"player": {}, "quests": {"quests": []}}
    data = migrate_save_dict(data)
    assert data["schema_version"] == CURRENT_SAVE_SCHEMA
    assert data.get("story_asset_version") == STORY_ASSET_VERSION
    assert data.get("companions") == []
    assert data.get("pending_companion_offer") is None
    assert data.get("flavor_log") == []
    assert data.get("stat_counters") == {}
    assert data.get("meta_break_budget") == 3
    p = data["player"]
    assert p.get("dimensional_fragments") == 0
    assert p.get("is_mancelled") is False
    assert data.get("repair_history") == []


def test_v5_migrates_dimentional_typo_on_items() -> None:
    data: dict = {
        "schema_version": 4,
        "story_asset_version": STORY_ASSET_VERSION,
        "player": {
            "inventory": {
                "max_slots": 20,
                "items": [{"item_id": "x", "dimentional_origin": "mold", "meta": {}}],
            }
        },
    }
    data = migrate_save_dict(data)
    assert data["schema_version"] == 5
    it = data["player"]["inventory"]["items"][0]
    assert it.get("dimensional_origin") == "mold"
    assert "dimentional_origin" not in it
