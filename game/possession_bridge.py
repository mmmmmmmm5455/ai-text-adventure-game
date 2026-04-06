"""
遊戲狀態 → 奪舍 / 快照池（PostgreSQL）的薄適配層。
需在 .env 設置 DATABASE_URL 並安裝 psycopg2-binary；帳戶與 player_id 由宿主應用建立。
"""

from __future__ import annotations

import os
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from game.game_state import GameState


def resolve_possession_player_id(explicit: str | None = None) -> uuid.UUID | None:
    """從參數或環境變量 POSSESSION_PLAYER_ID 解析 PostgreSQL 中的 players.player_id。"""
    raw = (explicit if explicit is not None else os.environ.get("POSSESSION_PLAYER_ID")) or ""
    raw = str(raw).strip()
    if not raw:
        return None
    try:
        return uuid.UUID(raw)
    except ValueError:
        return None


def upload_snapshot_from_game_state(
    player_id: uuid.UUID,
    state: GameState,
    *,
    label: str | None = None,
    recent_events: list[dict[str, Any]] | None = None,
    last_words: str | None = None,
    generate_last_words_llm: Any | None = None,
) -> uuid.UUID | None:
    """
    將當前 GameState 上傳為 player_snapshots 一行。
    generate_last_words_llm：若提供且 last_words 為 None，則調用其 generate_text 生成遺言。
    """
    from database.possession_db import PossessionDB, SnapshotService, possession_backend_ready

    if not possession_backend_ready():
        return None
    if state is None or state.player is None:
        return None

    data = state.to_dict()
    lw = last_words
    if lw is None and generate_last_words_llm is not None:
        lw = SnapshotService().generate_last_words(data, generate_last_words_llm)

    db = PossessionDB()
    return db.create_snapshot(
        player_id,
        data,
        label=label,
        recent_events=recent_events,
        last_words=lw,
    )
