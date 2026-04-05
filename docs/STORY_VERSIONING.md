# 剧情资产版本化与迁移策略

## 目标

- **剧情资产**（场景 ID、NPC、任务、物品、结局规则）与**存档**（`GameState` JSON）独立演进，但能追溯兼容性与升级路径。
- 定位：**作品集 demo** + 可维护；重大重构时再引入独立剧情包仓库亦可沿用同一策略。

## 版本号

| 名称 | 位置 | 含义 |
|------|------|------|
| `STORY_ASSET_VERSION` | `story/manifest.py` | 当前代码内嵌世界（宁静村庄）的语义化版本 `MAJOR.MINOR.PATCH` |
| `schema_version` | 存档 JSON 顶层 | 存档文件结构版本整数，由 `game/save_migrations.py` 中 `CURRENT_SAVE_SCHEMA` 定义 |

## 变更准则

- **MAJOR（剧情资产）**：场景/任务/NPC **ID 重命名或删除**、旧存档无法合理映射 → 递增 MAJOR，并在本文档「迁移说明」中记录；必要时提供一次性迁移脚本或「旧档仅只读」策略。
- **MINOR**：新增场景/NPC/任务、向后兼容 → 递增 MINOR。
- **PATCH**：文案、数值、提示词模板 → 递增 PATCH。

## 存档迁移

- 读档时：`GameState.from_dict` 先调用 `migrate_save_dict`，补齐 `schema_version` / `story_asset_version` 等字段。
- 当 `CURRENT_SAVE_SCHEMA` 递增时，在 `game/save_migrations.py` 中实现 `vN → vN+1` 的步骤（仅改 dict，不做 IO）。

## 与 CI 的关系

- GitHub Actions（`.github/workflows/ci.yml`）在推送与 PR 上运行 `pytest`，避免迁移逻辑回归。

## 未来可选：外置剧情包

若剧情改为 JSON/YAML 文件：

1. 在包根增加 `manifest.json`：`story_asset_version`、`min_engine_version`。
2. 启动时校验版本；不兼容则拒绝加载并提示升级引擎或降级资产包。
3. 迁移脚本放在 `scripts/migrate_story_*.py`，由发行说明引用。
