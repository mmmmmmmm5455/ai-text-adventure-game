# 项目概要

## 模块

| 目录 | 说明 |
|------|------|
| `core/` | 配置、日志、异常 |
| `game/` | 状态、玩家、背包、任务 |
| `engine/` | LLM 客户端、剧情、对话、记忆、事件 |
| `story/` | 默认世界「宁静村庄」数据 |
| `frontend/` | Streamlit UI 与组件 |
| `utils/` | 校验与 IO 辅助 |
| `tests/` | pytest 用例 |
| `docs/` | 开发与部署文档 |

## Phase 1 状态

已实现：单存档位、探索/对话、Chroma 记忆、LangGraph 场景生成节点、存档 JSON、基础测试。

## 工程化（作品集 demo）

- **CI**：`.github/workflows/ci.yml`（`pytest`，Python 3.11 / 3.12）。
- **剧情与存档版本**：`story/manifest.py`、`game/save_migrations.py`，详见 `docs/STORY_VERSIONING.md`。
- **i18n 预留**：`docs/I18N.md`。

## Phase 2+（规划）

多存档位、战斗、多语言、配图等（见 `CURSOR_PRO_MASTER_PROMPT.md` 路线图）。
