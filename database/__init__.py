"""資料庫適配（可選 PostgreSQL 快照池）。"""

from database.possession_db import PossessionDB, possession_backend_ready

__all__ = ["PossessionDB", "possession_backend_ready"]
