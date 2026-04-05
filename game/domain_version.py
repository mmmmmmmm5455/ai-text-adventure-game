"""
領域模型／存檔語意版本（與 JSON schema_version 搭配使用）。

- `schema_version`（save_migrations）：檔案欄位相容與遷移管線。
- `GAME_STATE_DOMAIN_VERSION`：領域聚合語意變更（例如同伴由 list[dict] 改為強型別快照）
  時遞增；每次遞增須在 save_migrations 中實作對應步驟，並更新 docs/ARCHITECTURE_POLICY.md。

政策：避免無上限往 GameState 堆任意 dict；新子系統優先獨立快照型別 + 單一欄位承載。
"""

from __future__ import annotations

# 與 CURRENT_SAVE_SCHEMA 不同：此處標記「領域形狀」修訂，可低於或等於 schema 迭代節奏
GAME_STATE_DOMAIN_VERSION: int = 1
