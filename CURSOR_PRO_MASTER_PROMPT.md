# Cursor Pro：AI 文字冒险游戏引擎 — 主提示词（一键复制）

将 **「二、给 Cursor 的完整指令」** 整段复制到 Cursor Chat，并补一句：「按此规范在本工作区从零创建可运行项目，缺什么就创建什么。」

---

## 一、项目背景与规划（给人读，也可附在仓库 README）

### 1.1 项目定位

- **名称**：AI-Powered Text Adventure Game Engine（AI 驱动文字冒险游戏引擎）
- **用途**：个人 GitHub 作品集核心项目之一，面向 AI Agent、对话系统、游戏 AI 相关实习/岗位；强调可运行、可展示、架构清晰、技术点可讲清楚。
- **双目标**：
  1. **开箱即玩**：本地一键启动，浏览器游玩。
  2. **可扩展框架**：核心与内容分离；换世界主要靠配置与数据，而非改引擎核心。

### 1.2 核心玩法与设计原则

| 原则 | 说明 |
|------|------|
| 高自由度 | 探索 + 选择 + 与 NPC 对话，选择影响标签与结局 |
| 沉浸感 | 生成内容须符合默认世界观；长期记忆与对话上下文保持连贯 |
| 轻量 | Python + Streamlit，无强制云端 API |
| 隐私优先 | 默认全部本地（Ollama + 可选本地向量库） |
| 可扩展 | 配置驱动世界；引擎接口稳定，便于 Phase 2/3 |

### 1.3 分阶段路线图（实现优先级）

**Phase 1（本次必须落地）**

- 目录与模块划分符合下文「项目结构」。
- `game`：状态、玩家、背包、任务；存档/读档（至少单存档位 JSON）。
- `engine`：故事生成、选择处理、对话、记忆（Chroma）、LLM 统一客户端（Ollama）、事件占位或简化实现。
- `story`：默认「宁静村庄」世界（场景、NPC、物品、任务、结局配置）。
- `frontend`：Streamlit 主界面（探索 + 对话双模式、侧栏状态与日志）。
- 文档：`README`、`QUICKSTART`、`.env.example`、启动脚本（Windows + Unix）。
- 测试：至少覆盖 `game_state`、`player`、故事/对话关键路径的单元测试若干条（目标 ≥10 条用例）。

**Phase 2（架构预留，可不完整实现）**

- 多存档位、SD 配图、音效、多语言、移动端适配、轻量战斗。

**Phase 3（仅规划）**

- 联机、世界编辑器、工坊、TTS、更多世界模板。

### 1.4 技术亮点（实现与文档中要可讲）

- 本地 LLM（Ollama）+ 可选缓存降低重复调用。
- LangChain / LangGraph 组织剧情与对话流程（按依赖可行性选用，避免为堆砌而空壳）。
- Chroma 存长期记忆片段，检索增强生成。
- Pydantic 校验配置与状态；`loguru` + `rich` 便于调试与演示。

---

## 二、给 Cursor 的完整指令（复制从下一行「角色与任务」到「验收清单」为止）

```
角色与任务
你是资深 Python 工程师与游戏系统设计师。请在当前工作区从零创建「AI 文字冒险游戏引擎」项目，要求：可直接运行、无占位 TODO、无硬编码密钥、中文用户界面与中文注释（代码注释可用中文），并严格遵守下列技术栈与目录结构。

技术栈（不得擅自替换为核心其他框架）
- Python 3.9+
- Streamlit 1.31+；聊天 UI 可用 streamlit-chat 或等价 Streamlit 原生实现（若加依赖须写入 requirements.txt）
- LangChain 0.1+、LangGraph、langchain-community（按实际需要引入，须有真实调用链，禁止空文件）
- Ollama 本地模型（默认 llama3，可通过环境变量切换）
- ChromaDB：长期记忆存储
- Pydantic 2.6+、python-dotenv、loguru、rich、httpx

项目结构（必须创建；所有 Python 包目录含 __init__.py）
text-adventure-game/
├── README.md
├── README_EN.md（英文简介，可精简）
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml（可选但推荐）
├── pytest.ini
├── .env.example
├── .gitignore
├── LICENSE（MIT）
├── start.sh
├── start.bat
├── QUICKSTART.md
├── PROJECT_SUMMARY.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── core/
│   ├── __init__.py
│   ├── config.py          # 环境变量与路径
│   ├── logger.py          # loguru 初始化
│   └── exceptions.py      # 自定义异常（可选）
├── game/
│   ├── __init__.py
│   ├── constants.py
│   ├── game_state.py      # 场景、时间、回合、任务、关键选择、标签；to_dict/from_dict；save/load JSON
│   ├── player.py          # 职业四维成长、属性、装备、技能、经验升级
│   ├── inventory.py       # 背包上限 20、分类、使用/丢弃
│   └── quest_system.py    # 主支线、进度、奖励
├── engine/
│   ├── __init__.py
│   ├── llm_client.py      # Ollama 封装、重试、降级文案、可选简单缓存
│   ├── story_engine.py    # 场景描述、4-6 个选项、process_choice、结局生成
│   ├── ai_dialogue.py     # 开场/继续/结束、20 轮窗口、好感度与简单线索提取
│   ├── memory_manager.py  # Chroma 写入与检索
│   └── event_handler.py   # 随机或条件事件（可简化但须可运行）
├── story/
│   ├── __init__.py
│   ├── world_config.py
│   ├── scenes.py
│   ├── characters.py
│   ├── items.py
│   ├── quests.py
│   └── endings.py
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   ├── io_utils.py
│   └── text_utils.py
├── frontend/
│   ├── __init__.py
│   ├── app.py             # Streamlit 入口：渐变主题 CSS、三栏布局
│   ├── components/        # chat、scene、player_status、choices、quest_list 等拆分
│   └── pages/             # home、game、settings、archive（可用 st.navigation 或多页）
├── data/                  # .gitignore 忽略运行时数据
│   ├── saves/
│   ├── logs/
│   ├── chroma_db/
│   └── cache/
├── tests/
│   ├── __init__.py
│   ├── test_game_state.py
│   ├── test_player.py
│   ├── test_story_engine.py
│   └── test_ai_dialogue.py
└── docs/
    ├── API.md
    ├── DEPLOYMENT.md
    ├── CUSTOM_WORLD.md
    └── DEVELOPMENT.md

默认世界「宁静村庄」
- 背景：森林边缘中世纪村庄，森林异象，玩家调查真相。
- 场景至少包含：村庄广场、迷雾森林、古老山脉、山脚旅店、神秘洞穴；可增「地下遗迹」。
- NPC：长者、商人、隐士、矿工、旅店老板、守卫；性格与对话风格区分。
- 物品示例：治疗药水、古老钥匙、宝藏等。
- 结局至少 4～5 类：英雄、隐居、富商、冒险（远行）、悲剧；由关键选择与任务状态判定。

前端要求
- 左侧：生命/能量、等级、金币、位置、回合、时间段、已完成任务摘要。
- 中间：角色创建 → 探索（场景卡片 + 选择按钮）→ 对话模式（聊天）；顶部或侧栏：新游戏、保存、读取、设置、帮助。
- 右侧：事件日志、背包、进行中任务。
- LLM 加载时显示明确 loading；错误时友好提示，不崩溃。

安全与健壮性
- 用户输入长度限制与基本校验；异常捕获后记录日志并给用户可读说明。
- 无 API Key 依赖；Ollama 不可用时降级为规则化短文案或缓存模板，保证可演示。

编码规范
- PEP 8；类型注解完整；单行尽量 ≤120 字符。
- 配置来自环境变量（见 .env.example），禁止密钥写进仓库。

执行顺序建议
1. 生成目录与依赖文件，确保 pip install -r requirements.txt 成功。
2. 实现 core → game → engine（先 llm_client + story/ai 再 memory）→ story 数据 → frontend → tests。
3. 提供 Windows/Linux 启动方式：start.bat / start.sh 调用 streamlit run frontend/app.py。

验收清单（你必须自检并满足）
- [ ] streamlit run frontend/app.py 可启动，浏览器可完整走通：创建角色 → 探索 → 至少一次对话 → 保存/读取（若已实现）。
- [ ] pytest 无失败（或明确标记 skip 的仅外部服务且默认 CI 不依赖）。
- [ ] README 含安装 Ollama、拉模型、复制 .env、运行命令。
- [ ] 无未完成 TODO、无死代码导入导致运行失败。
```

---

## 三、使用方式

1. 在本机安装 [Ollama](https://ollama.com)，执行 `ollama pull llama3`（或你在 `.env` 中指定的模型）。
2. 在项目根目录：`python -m venv .venv`，激活后 `pip install -r requirements.txt`。
3. 复制 `.env.example` 为 `.env` 并按需修改。
4. **Windows**：双击或运行 `start.bat`；**macOS/Linux**：`chmod +x start.sh && ./start.sh`。
5. 浏览器打开终端提示的本地地址（默认 `http://localhost:8501`）。

---

## 四、与旧版提示词的差异说明

- 统一包名为 `__init__.py`（不是 `init.py`）。
- 合并「简化版」与「究极版」为一条可执行指令，避免 Cursor 在两种目录树之间摇摆。
- 明确 Phase 1 必做 vs Phase 2/3 预留，减少半成品。
- 强调 **Ollama 不可用时的降级**，保证作品集演示不断线。

---

## 五、许可证

本 `CURSOR_PRO_MASTER_PROMPT.md` 文件随仓库以 MIT 与项目同权发布即可；若仅作个人使用可随意修改措辞。
