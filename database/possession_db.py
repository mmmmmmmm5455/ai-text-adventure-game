"""
奪舍系統 — 數據庫 ORM 層
===========================
封裝所有與 PostgreSQL 的交互，
將玩家的 GameState 快照化、查詢、奪舍等操作抽象為乾淨的 Python API。

使用方式：
    from database.possession_db import PossessionDB, get_db

    db = get_db()
    db.create_player("alice", "愛麗絲", "hashed_pw")
    db.create_snapshot(player_id, game_state)          # 定時快照
    snapshots = db.list_claimable_snapshots()
    db.claim_snapshot(snapshot_id, new_player_id)
    events = db.get_snapshot_events(snapshot_id)

依賴：
    pip install psycopg2-binary
    # 環境變量：DATABASE_URL=postgresql://user:pass@host:5432/dbname（未設置時本模組不可用）
"""

from __future__ import annotations

import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterator

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

SNAPSHOT_INTERVAL_HOURS = 12       # 每隔多久自動快照
MAX_RECENT_EVENTS = 10            # 快照中保存的精選事件數量
MAX_CLAIMABLE_SNAPSHOTS = 50      # 奪舍列表最多顯示條目

# ---------------------------------------------------------------------------
# 異常
# ---------------------------------------------------------------------------


class PossessionError(Exception):
    """所有奪舍系統相關異常的基類。"""
    pass


class PlayerNotFound(PossessionError):
    pass


class SnapshotNotFound(PossessionError):
    pass


class SelfClaimError(PossessionError):
    pass


class AlreadyClaimedError(PossessionError):
    pass


def possession_backend_ready() -> bool:
    """是否已配置資料庫連線（僅檢查設定，不 import psycopg2）。"""
    from core.config import get_settings

    url = get_settings().database_url
    return bool(url and str(url).strip())


def _database_url() -> str:
    from core.config import get_settings

    url = get_settings().database_url
    if not url or not str(url).strip():
        raise PossessionError(
            "DATABASE_URL 未設置：請在 .env 中配置 PostgreSQL 連線，並安裝 psycopg2-binary。"
        )
    return str(url).strip()


# ---------------------------------------------------------------------------
# 數據傳輸對象（DTO）
# ---------------------------------------------------------------------------


@dataclass
class PlayerDTO:
    player_id: uuid.UUID
    username: str
    display_name: str
    email: str | None
    created_at: datetime
    last_active_at: datetime
    is_public: bool
    is_banned: bool
    privacy_opt_out: bool


@dataclass
class ClaimableSnapshotDTO:
    snapshot_id: uuid.UUID
    character_name: str
    character_level: int
    character_bg_name: str | None
    character_hp: int | None
    character_max_hp: int | None
    snapshot_time: datetime
    last_words: str | None
    recent_events: list[dict]
    game_chapter: int
    playtime_minutes: int
    host_display_name: str
    snapshot_label: str | None


@dataclass
class SnapshotDetailDTO:
    snapshot_id: uuid.UUID
    player_id: uuid.UUID
    character_json: dict
    character_name: str
    character_level: int
    character_bg_name: str | None
    snapshot_time: datetime
    recent_events: list[dict]
    last_words: str | None
    game_chapter: int
    playtime_minutes: int


@dataclass
class SnapshotEventDTO:
    event_id: uuid.UUID
    snapshot_id: uuid.UUID
    event_index: int
    event_type: str
    event_summary: str
    scene_id: str | None
    round_count: int | None
    metadata: dict


# ---------------------------------------------------------------------------
# 連接池管理
# ---------------------------------------------------------------------------

_pool: Any = None


def _get_pool() -> Any:
    global _pool
    if _pool is None:
        import psycopg2.pool

        _pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=_database_url(),
            connect_timeout=10,
        )
    return _pool


@contextmanager
def get_connection():
    """從池中獲取連接，自動歸還。"""
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


@contextmanager
def get_cursor(dict_cursor: bool = True):
    """帶游標的上下文管理器。"""
    from psycopg2.extras import RealDictCursor

    with get_connection() as conn:
        cursor_factory = RealDictCursor if dict_cursor else None
        with conn.cursor(cursor_factory=cursor_factory) as cur:
            yield cur


def get_db() -> "PossessionDB":
    """返回 PossessionDB 單例。"""
    return PossessionDB()


# ---------------------------------------------------------------------------
# 核心 ORM 類
# ---------------------------------------------------------------------------


class PossessionDB:
    """
    奪舍系統數據庫操作類。

    所有方法都調用 get_connection() / get_cursor() 獲取連接。
    錯誤時拋具體異常（PlayerNotFound, SnapshotNotFound 等）。
    """

    # =====================================================================
    # 玩家操作
    # =====================================================================

    def create_player(
        self,
        username: str,
        display_name: str,
        password_hash: str,
        email: str | None = None,
    ) -> uuid.UUID:
        """創建新玩家帳戶。"""
        with get_cursor() as cur:
            cur.execute(
                """
                INSERT INTO players (username, display_name, password_hash, email)
                VALUES (%s, %s, %s, %s)
                RETURNING player_id
                """,
                (username, display_name, password_hash, email),
            )
            row = cur.fetchone()
            return row["player_id"]

    def get_player(self, player_id: uuid.UUID) -> PlayerDTO:
        """根據 ID 查詢玩家。"""
        with get_cursor() as cur:
            cur.execute(
                "SELECT * FROM players WHERE player_id = %s AND is_deleted = FALSE",
                (str(player_id),),
            )
            row = cur.fetchone()
            if not row:
                raise PlayerNotFound(f"玩家不存在：{player_id}")
            return self._row_to_player(row)

    def get_player_by_username(self, username: str) -> PlayerDTO:
        with get_cursor() as cur:
            cur.execute(
                "SELECT * FROM players WHERE username = %s AND is_deleted = FALSE",
                (username,),
            )
            row = cur.fetchone()
            if not row:
                raise PlayerNotFound(f"玩家不存在：{username}")
            return self._row_to_player(row)

    def set_privacy_opt_out(self, player_id: uuid.UUID, opt_out: bool) -> None:
        """設置是否參與快照池。"""
        with get_cursor() as cur:
            cur.execute(
                """
                UPDATE players
                   SET privacy_opt_out = %s
                 WHERE player_id = %s
                """,
                (opt_out, str(player_id)),
            )

    def list_players(self, limit: int = 50, offset: int = 0) -> Iterator[PlayerDTO]:
        """列出所有玩家（分頁）。"""
        with get_cursor() as cur:
            cur.execute(
                """
                SELECT * FROM players
                 WHERE is_deleted = FALSE
                 ORDER BY last_active_at DESC
                 LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            for row in cur:
                yield self._row_to_player(row)

    # =====================================================================
    # 快照操作
    # =====================================================================

    def create_snapshot(
        self,
        player_id: uuid.UUID,
        game_state_dict: dict,
        *,
        label: str | None = None,
        recent_events: list[dict] | None = None,
        last_words: str | None = None,
    ) -> uuid.UUID:
        """
        為玩家創建一個新的角色快照。

        :param player_id: 玩家 ID
        :param game_state_dict: GameState.to_dict() 的結果
        :param label: 可選的快照標籤（如「第3章-森林」）
        :param recent_events: 精選事件列表（最多 MAX_RECENT_EVENTS 條）
        :param last_words: AI 生成的遺言
        """
        p = game_state_dict.get("player", {})
        # 精簡版 JSON（只保存必要欄位，節省空間）
        character_json = self._extract_character_summary(game_state_dict)

        recent = (recent_events or [])[:MAX_RECENT_EVENTS]
        snapshot_time = datetime.now(timezone.utc)
        chapter, play_mins = _derive_chapter_and_playtime(game_state_dict)

        with get_cursor() as cur:
            cur.execute(
                """
                INSERT INTO player_snapshots (
                    player_id, snapshot_label, snapshot_time,
                    character_json, character_name, character_level,
                    character_bg_name, character_hp, character_max_hp,
                    recent_events, last_words,
                    game_chapter, playtime_minutes
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING snapshot_id
                """,
                (
                    str(player_id),
                    label,
                    snapshot_time,
                    json.dumps(character_json, ensure_ascii=False),
                    p.get("name", "無名"),
                    p.get("level", 1),
                    p.get("background_name"),
                    p.get("hp"),
                    p.get("max_hp"),
                    json.dumps(recent, ensure_ascii=False),
                    last_words,
                    chapter,
                    play_mins,
                ),
            )
            row = cur.fetchone()
            return row["snapshot_id"]

    def create_snapshot_from_summary(
        self,
        player_id: uuid.UUID,
        character_json: dict,
        *,
        label: str | None = None,
        recent_events: list[dict] | None = None,
        last_words: str | None = None,
        game_chapter: int = 1,
        playtime_minutes: int = 0,
    ) -> uuid.UUID:
        """
        直接用精簡角色數據創建快照（不需要完整的 GameState）。
        """
        recent = (recent_events or [])[:MAX_RECENT_EVENTS]
        with get_cursor() as cur:
            cur.execute(
                """
                INSERT INTO player_snapshots (
                    player_id, snapshot_label, snapshot_time,
                    character_json, character_name, character_level,
                    character_bg_name, character_hp, character_max_hp,
                    recent_events, last_words, game_chapter, playtime_minutes
                )
                VALUES (%s,%s,NOW(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING snapshot_id
                """,
                (
                    str(player_id),
                    label,
                    json.dumps(character_json, ensure_ascii=False),
                    character_json.get("name", "無名"),
                    character_json.get("level", 1),
                    character_json.get("background_name"),
                    character_json.get("hp"),
                    character_json.get("max_hp"),
                    json.dumps(recent, ensure_ascii=False),
                    last_words,
                    game_chapter,
                    playtime_minutes,
                ),
            )
            return cur.fetchone()["snapshot_id"]

    def get_snapshot(self, snapshot_id: uuid.UUID) -> SnapshotDetailDTO:
        """獲取快照詳情（含完整 character_json）。"""
        with get_cursor() as cur:
            cur.execute(
                """
                SELECT * FROM player_snapshots
                 WHERE snapshot_id = %s AND is_deleted = FALSE
                """,
                (str(snapshot_id),),
            )
            row = cur.fetchone()
            if not row:
                raise SnapshotNotFound(f"快照不存在：{snapshot_id}")
            return self._row_to_snapshot_detail(row)

    def list_my_snapshots(
        self,
        player_id: uuid.UUID,
        include_claimed: bool = True,
    ) -> list[SnapshotDetailDTO]:
        """列出玩家自己的快照歷史。"""
        with get_cursor() as cur:
            if include_claimed:
                cur.execute(
                    """
                    SELECT * FROM player_snapshots
                     WHERE player_id = %s AND is_deleted = FALSE
                     ORDER BY snapshot_time DESC
                    """,
                    (str(player_id),),
                )
            else:
                cur.execute(
                    """
                    SELECT * FROM player_snapshots
                     WHERE player_id = %s AND is_deleted = FALSE AND is_claimed = FALSE
                     ORDER BY snapshot_time DESC
                    """,
                    (str(player_id),),
                )
            return [self._row_to_snapshot_detail(row) for row in cur]

    def list_claimable_snapshots(
        self,
        limit: int = MAX_CLAIMABLE_SNAPSHOTS,
        min_level: int = 1,
        max_level: int = 999,
        search_name: str | None = None,
        exclude_player_id: uuid.UUID | None = None,
    ) -> list[ClaimableSnapshotDTO]:
        """
        列出可供奪舍的快照（公開、未認領）。

        :param limit: 返回數量上限
        :param min_level / max_level: 等級範圍過濾
        :param search_name: 角色名模糊搜索（ILIKE）
        :param exclude_player_id: 排除某玩家（如新玩家想排除自己的）
        """
        with get_cursor() as cur:
            params: list = []
            where_clauses = [
                "s.is_deleted = FALSE",
                "s.is_claimed = FALSE",
                "p.is_public = TRUE",
                "p.is_banned = FALSE",
                "p.is_deleted = FALSE",
                "p.privacy_opt_out = FALSE",
                "s.character_level BETWEEN %s AND %s",
            ]
            params.extend([min_level, max_level])

            if search_name:
                where_clauses.append("s.character_name ILIKE %s")
                params.append(f"%{search_name}%")

            if exclude_player_id:
                where_clauses.append("s.player_id != %s")
                params.append(str(exclude_player_id))

            where_sql = " AND ".join(where_clauses)
            query = f"""
                SELECT s.*, p.display_name AS host_display_name
                  FROM player_snapshots s
                  JOIN players p ON p.player_id = s.player_id
                 WHERE {where_sql}
                 ORDER BY s.snapshot_time DESC
                 LIMIT %s
            """
            params.append(limit)
            cur.execute(query, params)
            return [self._row_to_claimable(row) for row in cur]

    def claim_snapshot(
        self,
        snapshot_id: uuid.UUID,
        new_player_id: uuid.UUID,
    ) -> SnapshotDetailDTO:
        """
        奪舍：將快照標記為已認領，並返回完整數據供加載。
        會同時創建一條 possession_records。

        :raises SnapshotNotFound: 快照不存在
        :raises AlreadyClaimedError: 已被別人奪舍
        :raises SelfClaimError: 不能奪舍自己的快照
        """
        with get_cursor() as cur:
            # 先查快照信息（校驗 + 獲取原 player_id）
            cur.execute(
                """
                SELECT s.*, p.player_id AS host_player_id_raw
                  FROM player_snapshots s
                  JOIN players p ON p.player_id = s.player_id
                 WHERE s.snapshot_id = %s AND s.is_deleted = FALSE
                """,
                (str(snapshot_id),),
            )
            row = cur.fetchone()
            if not row:
                raise SnapshotNotFound(f"快照不存在：{snapshot_id}")
            if row["is_claimed"]:
                raise AlreadyClaimedError(f"快照已被奪舍：{snapshot_id}")

            host_player_id = row["host_player_id_raw"]
            if str(host_player_id) == str(new_player_id):
                raise SelfClaimError("不能奪舍自己的快照")

            # 更新快照狀態
            cur.execute(
                """
                UPDATE player_snapshots
                   SET is_claimed = TRUE,
                       claimed_by_player_id = %s,
                       claimed_at = NOW()
                 WHERE snapshot_id = %s
                """,
                (str(new_player_id), str(snapshot_id)),
            )

            # 記錄奪舍
            cur.execute(
                """
                INSERT INTO possession_records (host_snapshot_id, host_player_id, possessor_player_id)
                VALUES (%s, %s, %s)
                """,
                (str(snapshot_id), str(host_player_id), str(new_player_id)),
            )

        return self.get_snapshot(snapshot_id)

    def delete_snapshot(self, snapshot_id: uuid.UUID, player_id: uuid.UUID) -> None:
        """軟刪除快照（玩家只能刪自己的）。"""
        with get_cursor() as cur:
            cur.execute(
                """
                UPDATE player_snapshots
                   SET is_deleted = TRUE, deleted_at = NOW()
                 WHERE snapshot_id = %s AND player_id = %s
                """,
                (str(snapshot_id), str(player_id)),
            )
            if cur.rowcount == 0:
                raise SnapshotNotFound(f"快照不存在或無權限：{snapshot_id}")

    def prune_old_snapshots(self, player_id: uuid.UUID, keep_last: int = 5) -> int:
        """
        清理舊快照：每個玩家最多保留最近 N 個未認領快照。
        返回刪除數量。
        """
        with get_cursor() as cur:
            cur.execute(
                """
                WITH ranked AS (
                    SELECT snapshot_id,
                           ROW_NUMBER() OVER (
                               PARTITION BY player_id
                               ORDER BY snapshot_time DESC
                           ) AS rn
                      FROM player_snapshots
                     WHERE player_id = %s
                       AND is_deleted = FALSE
                       AND is_claimed = FALSE
                )
                DELETE FROM player_snapshots
                 WHERE snapshot_id IN (
                       SELECT snapshot_id FROM ranked WHERE rn > %s
                 )
                """,
                (str(player_id), keep_last),
            )
            return cur.rowcount

    # =====================================================================
    # 快照事件操作
    # =====================================================================

    def add_snapshot_event(
        self,
        snapshot_id: uuid.UUID,
        event_index: int,
        event_type: str,
        event_summary: str,
        *,
        scene_id: str | None = None,
        round_count: int | None = None,
        metadata: dict | None = None,
    ) -> uuid.UUID:
        """為快照添加一個精選事件。"""
        with get_cursor() as cur:
            cur.execute(
                """
                INSERT INTO snapshot_events (
                    snapshot_id, event_index, event_type,
                    event_summary, scene_id, round_count, metadata
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                RETURNING event_id
                """,
                (
                    str(snapshot_id),
                    event_index,
                    event_type,
                    event_summary,
                    scene_id,
                    round_count,
                    json.dumps(metadata or {}, ensure_ascii=False),
                ),
            )
            return cur.fetchone()["event_id"]

    def get_snapshot_events(
        self,
        snapshot_id: uuid.UUID,
        event_type: str | None = None,
    ) -> list[SnapshotEventDTO]:
        """獲取快照的所有精選事件（用於殘響系統）。"""
        with get_cursor() as cur:
            if event_type:
                cur.execute(
                    """
                    SELECT * FROM snapshot_events
                     WHERE snapshot_id = %s AND event_type = %s
                     ORDER BY event_index ASC
                    """,
                    (str(snapshot_id), event_type),
                )
            else:
                cur.execute(
                    """
                    SELECT * FROM snapshot_events
                     WHERE snapshot_id = %s
                     ORDER BY event_index ASC
                    """,
                    (str(snapshot_id),),
                )
            return [self._row_to_event(row) for row in cur]

    # =====================================================================
    # 輔助查詢
    # =====================================================================

    def get_continuation_count(self, snapshot_id: uuid.UUID) -> int:
        """查詢某快照被多少新玩家繼續過。"""
        with get_cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS cnt FROM possession_records
                 WHERE host_snapshot_id = %s
                """,
                (str(snapshot_id),),
            )
            return cur.fetchone()["cnt"]

    def get_possessor_history(
        self,
        player_id: uuid.UUID,
    ) -> list[dict]:
        """查詢某玩家奪舍過的快照歷史。"""
        with get_cursor() as cur:
            cur.execute(
                """
                SELECT pr.*, s.character_name, s.character_level
                  FROM possession_records pr
                  LEFT JOIN player_snapshots s ON s.snapshot_id = pr.host_snapshot_id
                 WHERE pr.possessor_player_id = %s
                 ORDER BY pr.possessed_at DESC
                """,
                (str(player_id),),
            )
            return [dict(row) for row in cur]

    # =====================================================================
    # 私有轉換方法
    # =====================================================================

    @staticmethod
    def _row_to_player(row: dict) -> PlayerDTO:
        return PlayerDTO(
            player_id=row["player_id"],
            username=row["username"],
            display_name=row["display_name"],
            email=row["email"],
            created_at=row["created_at"],
            last_active_at=row["last_active_at"],
            is_public=row["is_public"],
            is_banned=row["is_banned"],
            privacy_opt_out=bool(row.get("privacy_opt_out", False)),
        )

    @staticmethod
    def _row_to_snapshot_detail(row: dict) -> SnapshotDetailDTO:
        return SnapshotDetailDTO(
            snapshot_id=row["snapshot_id"],
            player_id=row["player_id"],
            character_json=json.loads(row["character_json"])
            if isinstance(row["character_json"], str)
            else row["character_json"],
            character_name=row["character_name"],
            character_level=row["character_level"],
            character_bg_name=row["character_bg_name"],
            snapshot_time=row["snapshot_time"],
            recent_events=json.loads(row["recent_events"])
            if isinstance(row["recent_events"], str)
            else row["recent_events"],
            last_words=row["last_words"],
            game_chapter=row["game_chapter"],
            playtime_minutes=row["playtime_minutes"],
        )

    @staticmethod
    def _row_to_claimable(row: dict) -> ClaimableSnapshotDTO:
        return ClaimableSnapshotDTO(
            snapshot_id=row["snapshot_id"],
            character_name=row["character_name"],
            character_level=row["character_level"],
            character_bg_name=row["character_bg_name"],
            character_hp=row["character_hp"],
            character_max_hp=row["character_max_hp"],
            snapshot_time=row["snapshot_time"],
            last_words=row["last_words"],
            recent_events=json.loads(row["recent_events"])
            if isinstance(row["recent_events"], str)
            else row["recent_events"],
            game_chapter=row["game_chapter"],
            playtime_minutes=row["playtime_minutes"],
            host_display_name=row["host_display_name"],
            snapshot_label=row["snapshot_label"],
        )

    @staticmethod
    def _row_to_event(row: dict) -> SnapshotEventDTO:
        return SnapshotEventDTO(
            event_id=row["event_id"],
            snapshot_id=row["snapshot_id"],
            event_index=row["event_index"],
            event_type=row["event_type"],
            event_summary=row["event_summary"],
            scene_id=row["scene_id"],
            round_count=row["round_count"],
            metadata=json.loads(row["metadata"])
            if isinstance(row["metadata"], str)
            else row["metadata"],
        )

    @staticmethod
    def _extract_character_summary(game_state_dict: dict) -> dict:
        """
        從完整的 GameState.to_dict() 中提取精簡的角色摘要。
        只保留快照需要的核心字段（節省 JSONB 存儲空間）。
        """
        player = game_state_dict.get("player", {})
        return {
            "name": player.get("name"),
            "gender": player.get("gender"),
            "level": player.get("level", 1),
            "hp": player.get("hp"),
            "max_hp": player.get("max_hp"),
            "mp": player.get("mp"),
            "max_mp": player.get("max_mp"),
            "gold": player.get("gold", 0),
            "profession": player.get("profession"),
            "background_id": player.get("background_id"),
            "background_name": player.get("background_name"),
            "traits": player.get("traits", []),
            "stats": {
                "strength": player.get("strength"),
                "intelligence": player.get("intelligence"),
                "agility": player.get("agility"),
                "charisma": player.get("charisma"),
                "perception": player.get("perception"),
                "endurance": player.get("endurance"),
            },
            "inventory_item_ids": [
                item["item_id"]
                for item in player.get("inventory", {}).get("items", [])
            ],
            "equipped_weapon_id": player.get("equipped_weapon_id"),
            "equipped_armor_id": player.get("equipped_armor_id"),
            "skills": player.get("skills", []),
            "companion_ids": [
                c.get("companion_id") for c in game_state_dict.get("companions", [])
            ],
            "current_scene_id": game_state_dict.get("current_scene_id"),
            "chapter": _derive_chapter_and_playtime(game_state_dict)[0],
        }


def _derive_chapter_and_playtime(game_state_dict: dict) -> tuple[int, int]:
    """從存檔 JSON 推導 game_chapter（SMALLINT）與 playtime_minutes（粗略：約等于回合數）。"""
    rnd = int(game_state_dict.get("round_count") or 0)
    wf = game_state_dict.get("world_flags") or {}
    raw_ch = wf.get("story_chapter") if isinstance(wf, dict) else None
    try:
        chapter = int(raw_ch) if raw_ch is not None else max(1, min(32767, 1 + rnd // 40))
    except (TypeError, ValueError):
        chapter = max(1, min(32767, 1 + rnd // 40))
    chapter = max(1, min(32767, chapter))
    play_mins = max(0, min(2_147_483_647, rnd))
    return chapter, play_mins


# ---------------------------------------------------------------------------
# 便捷封裝（整合遊戲引擎）
# ---------------------------------------------------------------------------


class SnapshotService:
    """
    遊戲引擎與數據庫之間的高層封裝。
    使用時直接操作這個類，而不是直接調 PossessionDB。
    """

    def __init__(self, db: PossessionDB | None = None):
        self.db = db or get_db()

    def take_periodic_snapshot(
        self,
        player_id: uuid.UUID,
        game_state_dict: dict,
    ) -> uuid.UUID | None:
        """
        定時快照：每 SNAPSHOT_INTERVAL_HOURS 執行一次。
        如果玩家設置了隱私退出，則跳過。
        """
        try:
            player = self.db.get_player(player_id)
            if player.privacy_opt_out:
                return None
        except PlayerNotFound:
            return None

        return self.db.create_snapshot(
            player_id=player_id,
            game_state_dict=game_state_dict,
            label=f"自動存檔",
        )

    def build_memory_for_llm(
        self,
        snapshot_id: uuid.UUID,
        llm_client,
        max_events: int = 5,
    ) -> str:
        """
        根據快照事件構建一段 LLM Prompt 用的「記憶摘要」。
        用於殘響系統中展示給新玩家。

        :param snapshot_id: 快照 ID
        :param llm_client: 引擎中的 LLM 客戶端
        :param max_events: 最多使用的事件數
        :return: 一段文字記憶描述
        """
        snapshot = self.db.get_snapshot(snapshot_id)
        events = snapshot.recent_events[:max_events]

        if not events:
            return f"「{snapshot.character_name}」的故事沒有留下太多痕迹……"

        event_texts = "\n".join(
            f"- {e.get('summary', str(e))}" for e in events
        )

        prompt = f"""以下是一名冒險者的生活片段：
{event_texts}

請用第一人稱，以大約80字寫一段「這個人的回憶片段」，
語氣可以是：溫暖的、遺憾的、憤怒的、或平靜的。
"""
        try:
            return llm_client.generate_text(prompt, temperature=0.7, max_tokens=200)
        except Exception:
            return f"「{snapshot.character_name}」似乎有什麼心事……"

    def generate_last_words(
        self,
        game_state_dict: dict,
        llm_client,
    ) -> str | None:
        """
        遊戲結束/角色死亡時，調用大模型生成一句「遺言」。
        """
        player = game_state_dict.get("player", {})
        recent = game_state_dict.get("game_log", [])[-5:]

        if not recent:
            return None

        events_text = "\n".join(f"- {e}" for e in recent)
        prompt = f"""以下是某冒險者的最後經歷：
{events_text}

請以第三人稱寫一句簡短的「告別話」（20字以內），
表達這個人對冒險生涯的態度。可以是：
- 留戀：「這一生，我沒有後悔。」
- 憤怒：「終有一天，會有人替我報仇。」
- 平靜：「累了……終於可以休息了。」
"""
        try:
            return llm_client.generate_text(prompt, temperature=0.8, max_tokens=50)
        except Exception:
            return None
