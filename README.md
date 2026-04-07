# AI 文字冒险游戏引擎

本地 **Ollama** + **Streamlit** 驱动的文字冒险游戏：动态场景描写、NPC 对话（LangChain）、长期记忆（Chroma）、任务与多结局。

## 功能概览

- **探索模式**：场景描写（LangGraph 组织单次生成）、移动、搜寻、休息、结局判定  
- **对话模式**：与 NPC 聊天，好感度与记忆片段  
- **存档**：`data/saves/slot1.json`  
- **离线降级**：Ollama 不可用时使用规则化叙事，保证可演示

## 数据库系统

- **奪舍系统**：PostgreSQL 数据库存储角色快照，支持奪舍功能
- **存档管理**：数据库化存档，多存档位支持
- **配置要求**：PostgreSQL 11+，可选依赖（无数据库时游戏仍可运行）

**配置方法：**  
1. 安装 PostgreSQL  
2. 创建数据库和用户  
3. 配置 .env 文件  
4. 运行 `python tools/init_database.py`

**详细指南：** `docs/POSTGRESQL_SETUP_GUIDE.md`

**离线模式：** 无数据库时游戏仍可运行，但奪舍功能不可用。

## 环境要求

- Python 3.9+（已在 3.13 下测试）
- [Ollama](https://ollama.com/)（可选但强烈推荐）
- PostgreSQL 11+（可选，用于奪舍系统）

## 快速开始

```powershell
cd ai_text_advanture_game
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
ollama pull llama3
ollama pull nomic-embed_text
```

### 数据库配置（可选，奪舍系统需要）

```powershell
# 1. 安装 PostgreSQL
# Windows: 下载并运行 PostgreSQL Installer
# macOS: brew install postgresql
# Linux: sudo apt-get install postgresql postgresql-contrib

# 2. 创建数据库和用户
psql -U postgres
CREATE DATABASE text_adventure;
CREATE USER game_user WITH PASSWORD '你的密码';
GRANT ALL PRIVILEGES ON DATABASE text_adventure TO game_user;
\q

# 3. 配置 .env 文件
DATABASE_URL=postgresql://game_user:你的密码@127.0.0.1:5432/text_adventure

# 4. 安装依赖
pip install psycopg2-binary

# 5. 初始化数据库
python tools/init_database.py
```

**详细说明：** `docs/POSTGRESQL_SETUP_GUIDE.md`

启动（Windows，**推荐**与 `start.bat` 一致）：

```powershell
$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"
python -m streamlit run frontend/app.py
```

说明：**勿写**裸命令 `streamlit run ...`（未装全局脚本时会找不到命令）；`PYTHONIOENCODING` 可减少 PowerShell 默认 `cp950` 下中文输出报错。

或直接双击 / 运行 **`start.bat`**（已设置 `PYTHONPATH`、`PYTHONIOENCODING` 与 `python -m streamlit`）。

macOS / Linux：

```bash
chmod +x start.sh
export PYTHONPATH="$PWD"
export PYTHONIOENCODING=UTF-8
./start.sh
```

浏览器访问终端提示的地址（默认 `http://localhost:8501`）。

**中文逐步教程（如何打开游戏、Docker、常见问题）：** 见 **`docs/TUTORIAL_CN.md`**。

## 测试与 CI

```bash
pip install -r requirements-dev.txt
python -m pytest tests -q
```

- **默认测试不依赖 Ollama**；契约测试在 `tests/contracts/`（`TextGenerationPort` 与 `LLMClient`）。
- **可选真实 LLM 集成**：`set RUN_LLM_INTEGRATION=1` 后运行 `tests/integration/`。
- 工程政策（作品集 / Docker / 存档领域版本）：见 **`docs/ARCHITECTURE_POLICY.md`**。
- 已知问题、已修复项与残余风险：**`docs/EVALUATION_REPORT.md`**。

推送到 GitHub 后，`.github/workflows/ci.yml` 会在 `main`/`master` 的推送与 PR 上运行相同测试（Python 3.11、3.12）。在仓库 **Settings → Actions** 中启用 Actions 即可。

## Docker

```bash
docker compose up --build
```

浏览器访问 `http://localhost:8501`。Ollama 建议在**宿主机**运行，容器内已通过 `OLLAMA_BASE_URL=http://host.docker.internal:11434` 指向宿主（Docker Desktop Windows/Mac）。Linux 宿主请改为实际网关 IP 或使用 `network_mode: host` 等方案，详见 `docs/ARCHITECTURE_POLICY.md`。

## 目录结构

见仓库内 `PROJECT_SUMMARY.md` 与 `docs/DEVELOPMENT.md`。

## 剧情资产与存档版本

- 剧情资产版本：`story/manifest.py` 中 `STORY_ASSET_VERSION`
- 存档结构迁移：`game/save_migrations.py`
- 说明文档：`docs/STORY_VERSIONING.md`、`docs/I18N.md`

## 许可证

MIT，见 `LICENSE`。
