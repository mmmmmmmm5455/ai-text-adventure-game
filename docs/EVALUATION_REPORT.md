# 專案執行與架構評估報告

本文記錄已知問題、已實作修復與殘餘風險；修復對應之程式變更可於 Git 歷史或下方「修復清單」對照。

---

## 1. 測試與 CI

| 項目 | 狀態 |
|------|------|
| `pytest tests`（預設不依賴 Ollama） | **132 passed, 1 skipped**（skipped：`streamlit.testing` 不可用時整頁煙霧） |
| GitHub Actions | 多 Python 版本；`actions/checkout@v6`、`setup-python@v6`（Node 24）；已設 `PYTHONIOENCODING=utf-8` |

---

## 2. 已修復問題（摘要）

| 領域 | 問題 | 修復 |
|------|------|------|
| Windows 主控台 | `cp950` 下中文 `print`/log 觸發 `UnicodeEncodeError` | `core/io_encoding.py`；`frontend/app.py` 入口呼叫；`tests/conftest.py`；`start.bat`/`start.sh`/`Dockerfile` 設 `PYTHONIOENCODING` |
| Chroma | 每個引擎各建 `MemoryManager`，重複初始化 | `shared_memory_manager()`；`StoryEngine` / `AIDialogueEngine` / `EnhancementEngine` 共用 |
| HTTP/Ollama | 服務未開時連線長時間掛起 | `OLLAMA_CONNECT_TIMEOUT` + `httpx.Timeout(connect=…)`（`LLMClient`、`ollama_embed_text`、`ChatOllama`） |
| 啟動指令 | 全域無 `streamlit` 可執行檔 | 統一 `python -m streamlit`；README / 教程 / `CURSOR_PRO_MASTER_PROMPT.md` |
| Docker Compose | 環境變數不完整 | `PYTHONIOENCODING`、`OLLAMA_TIMEOUT`、`OLLAMA_CONNECT_TIMEOUT` |
| 創角 | `build()` 強制戰士 | `build(profession=…)`，預設仍 `WARRIOR` |
| 創角 LLM | `quick_random` 吞掉所有例外 | `loguru` **warning** 記錄失敗原因 |
| 創角道具 | 未知 id / 背包滿時靜默失敗 | **warning** 日誌 |
| `new_game_state` | 無效職業時 `Enum` 錯誤難讀 | 包成明確 **`ValueError`（無效職業）** |

---

## 3. 殘餘風險與產品缺口（尚未改或僅部分支援）

| 風險 | 說明 | 建議後續 |
|------|------|----------|
| **Streamlit 與 `CharacterCreator` 脫鉤** | 首頁 `render_home` 仍走 `new_game_state` + 四職業；JSON 背景／特質創角未接入 UI | 增加「進階創角」頁或 API 將 `CharacterCreator.build()` 結果設為 `state.player` |
| **特質效果** | `Player.trait_effects` / `trait_effect()` 已寫入；戰鬥／骰子未必讀取 | 在結算處統一讀 `trait_effect("healing_bonus")` 等 |
| **`accept_llm_result` 清空特後** | 接受 LLM 背景會清空既有正負特質（設計上為「整包替換」） | 文件說明或改為可選「合併模式」 |
| **Ollama 仍為可選單點故障** | 場景／對話會重試後降級；體感延遲仍取決於網路與 `OLLAMA_TIMEOUT` | 監控 `health_check()`；必要時預設更短 read 逾時 |
| **E2E 瀏覽器測試** | 無 Playwright；僅可選 `streamlit.testing` 煙霧 | 按需引入 E2E |

---

## 4. 如何本地驗證

```powershell
$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"
python -m pytest tests -q
python -m streamlit run frontend/app.py
```

---

*最後更新：與儲存庫內 `pytest`、創角與啟動腳本行為對齊。詳見 `README.md`、`docs/TUTORIAL_CN.md`。*
