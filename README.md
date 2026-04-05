# AI 文字冒险游戏引擎

本地 **Ollama** + **Streamlit** 驱动的文字冒险游戏：动态场景描写、NPC 对话（LangChain）、长期记忆（Chroma）、任务与多结局。

## 功能概览

- **探索模式**：场景描写（LangGraph 组织单次生成）、移动、搜寻、休息、结局判定  
- **对话模式**：与 NPC 聊天，好感度与记忆片段  
- **存档**：`data/saves/slot1.json`  
- **离线降级**：Ollama 不可用时使用规则化叙事，保证可演示  

## 环境要求

- Python 3.9+（已在 3.13 下测试）  
- [Ollama](https://ollama.com/)（可选但强烈推荐）  

## 快速开始

```powershell
cd ai_text_advanture_game
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
ollama pull llama3
ollama pull nomic-embed-text
```

启动（Windows）：

```powershell
$env:PYTHONPATH = (Get-Location).Path
streamlit run frontend/app.py
```

或双击 / 运行 `start.bat`。

macOS / Linux：

```bash
chmod +x start.sh
export PYTHONPATH=$PWD
./start.sh
```

浏览器访问终端提示的地址（默认 `http://localhost:8501`）。

## 测试与 CI

```bash
pip install -r requirements-dev.txt
python -m pytest tests -q
```

推送到 GitHub 后，`.github/workflows/ci.yml` 会在 `main`/`master` 的推送与 PR 上运行相同测试（Python 3.11、3.12）。在仓库 **Settings → Actions** 中启用 Actions 即可。

## 目录结构

见仓库内 `PROJECT_SUMMARY.md` 与 `docs/DEVELOPMENT.md`。

## 剧情资产与存档版本

- 剧情资产版本：`story/manifest.py` 中 `STORY_ASSET_VERSION`
- 存档结构迁移：`game/save_migrations.py`
- 说明文档：`docs/STORY_VERSIONING.md`、`docs/I18N.md`

## 许可证

MIT，见 `LICENSE`。
