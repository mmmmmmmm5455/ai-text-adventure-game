"""奪舍 / 快照池：無資料庫時仍可導入；衍生欄位單元測試。"""

from __future__ import annotations


def test_derive_chapter_and_playtime() -> None:
    from database.possession_db import _derive_chapter_and_playtime

    assert _derive_chapter_and_playtime({"round_count": 0, "world_flags": {}}) == (1, 0)
    assert _derive_chapter_and_playtime({"round_count": 100, "world_flags": {"story_chapter": 3}}) == (
        3,
        100,
    )
    ch, pt = _derive_chapter_and_playtime({"round_count": 2_000_000, "world_flags": {}})
    assert ch == 32767
    assert pt == 2_000_000


def test_possession_backend_ready_is_bool() -> None:
    from database.possession_db import possession_backend_ready

    assert isinstance(possession_backend_ready(), bool)


def test_import_database_package() -> None:
    import database

    assert hasattr(database, "possession_backend_ready")
