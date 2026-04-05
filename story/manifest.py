"""
剧情资产版本：与代码中的场景/NPC/任务定义对齐，用于存档兼容性与迁移说明。

语义化版本 MAJOR.MINOR.PATCH：
- MAJOR：破坏性变更（场景 ID 重命名、任务 ID 变更、存档字段不兼容）
- MINOR：新增场景/NPC/任务或向后兼容的扩展
- PATCH：文案与数值微调
"""

from __future__ import annotations

# 当前仓库内嵌「宁静村庄」剧情资产版本（与 Python 模块 story.* 一致）
STORY_ASSET_VERSION: str = "1.0.0"
