# 架構與工程政策（作品集）

本文件對齊倉庫維護決策：**作品集展示**、**可 Docker 執行**、**CI 以離線測試為主**、**契約測試作閘道**、**存檔與領域版本分層**。

## 1. 產品定位

- **作品集 / Demo**：優先可運行、可複現、面試可講清楚架構取捨。
- 允許漸進重構；**新程式碼**應比舊程式碼更遵守依賴邊界（見 `core/ports.py`）。

## 2. Docker

- `Dockerfile`：容器內啟動 Streamlit，監聽 `0.0.0.0:8501`。
- `docker-compose.yml`：本機一鍵起服；可掛載 `./data` 以持久化存檔與 Chroma。
- **Ollama**：預設不在同一容器內（避免映像過重）；本機可另起 Ollama，並以環境變數 `OLLAMA_BASE_URL` 指向 `host.docker.internal`（Windows/Mac）或宿主 IP。

```bash
docker compose up --build
```

瀏覽器開 `http://localhost:8501`。若需模型，請在宿主安裝 Ollama 並 `ollama pull`。

## 3. 測試策略與「契約」

| 類型 | 要求 | CI |
|------|------|-----|
| **單元／整合（預設）** | **不依賴 Ollama**；可 mock HTTP 或依賴降級路徑 | ✅ `pytest tests/` |
| **契約測試** | `tests/contracts/`：`TextGenerationPort` 與 `LLMClient` 簽名／結構子型別 | ✅ 同上，納入 CI |
| **可選 LLM 整合** | 設 `RUN_LLM_INTEGRATION=1` 才跑 `tests/integration/` | ❌ 預設不跑 |

**原則**：預設 CI **必須綠**，且 **不得在預設管線中要求本機 Ollama**。

## 4. 依賴反轉（DIP）邊界

- **當前契約層**：`core/ports.TextGenerationPort` — 敘事文字生成與健康檢查。
- **實作**：`engine.llm_client.LMClient`（Ollama HTTP）。
- **演進**：新服務建構時應接受 `TextGenerationPort` 注入，便於測試假實作與更換後端。

## 5. 存檔相容與版本化領域模型

兩層版本：

1. **`schema_version`（`game/save_migrations.py`）**  
   JSON 欄位增刪、預設值補齊、舊檔升級。**每次改存檔形狀應遞增並寫遷移**。

2. **`GAME_STATE_DOMAIN_VERSION`（`game/domain_version.py`）**  
   領域語意變更（例如將鬆散 `dict` 聚合收斂為強型別快照、或拆分大欄位）。  
   遞增時必須：更新遷移、補測試、在本文件記一筆變更摘要。

**技術債上限（務實）**：

- 避免在 `GameState` 上無限新增 **無型別** `dict` 欄位；同一子系統若超過 **~3 個** 相關鬆散結構，應考慮 **單一快照型別**（dataclass / Pydantic）+ **一個** JSON 欄位承載。
- 新功能優先：**獨立快照 + 明確版本欄**（見各快照型別內），而非繼續堆平鋪鍵。

## 6. 與現有文檔的關係

- 劇情資產版本：`docs/STORY_VERSIONING.md`、`story/manifest.py`
- 開發說明：`docs/DEVELOPMENT.md`
