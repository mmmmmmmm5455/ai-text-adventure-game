"""
存档元数据系统：标签和描述
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
import json


@dataclass
class SaveMetadata:
    """存档元数据"""
    tags: list[str] = field(default_factory=list)
    description: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "tags": list(self.tags),
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SaveMetadata":
        """从字典创建"""
        return cls(
            tags=list(data.get("tags", [])),
            description=data.get("description", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )

    def add_tag(self, tag: str) -> None:
        """添加标签"""
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now().isoformat()

    def remove_tag(self, tag: str) -> None:
        """移除标签"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now().isoformat()

    def set_description(self, description: str) -> None:
        """设置描述"""
        self.description = description
        self.updated_at = datetime.now().isoformat()


def get_metadata_path(save_path: Path) -> Path:
    """获取存档元数据文件路径

    Args:
        save_path: 存档文件路径

    Returns:
        元数据文件路径
    """
    return save_path.with_suffix(".meta.json")


def load_metadata(save_path: Path) -> SaveMetadata:
    """加载存档元数据

    Args:
        save_path: 存档文件路径

    Returns:
        SaveMetadata 对象
    """
    meta_path = get_metadata_path(save_path)

    if not meta_path.exists():
        # 创建新的元数据
        return SaveMetadata(
            tags=[],
            description="",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return SaveMetadata.from_dict(data)
    except (OSError, json.JSONDecodeError):
        # 如果读取失败，返回空元数据
        return SaveMetadata(
            tags=[],
            description="",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )


def save_metadata(save_path: Path, metadata: SaveMetadata) -> None:
    """保存存档元数据

    Args:
        save_path: 存档文件路径
        metadata: 元数据对象
    """
    meta_path = get_metadata_path(save_path)

    try:
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata.to_dict(), f, ensure_ascii=False, indent=2)
    except OSError as e:
        raise IOError(f"保存元数据失败：{e}") from e


# 预定义标签列表
PREDEFINED_TAGS = [
    "主线任务",
    "支线任务",
    "探索",
    "战斗",
    "剧情分支",
    "低等级",
    "中等级",
    "高等级",
    "装备齐全",
    "资金充足",
    "特殊事件",
    "存档点",
    "重要选择",
    "速通",
    "完美通关",
]


def get_suggested_tags(save_data: dict[str, Any]) -> list[str]:
    """根据存档内容推荐标签

    Args:
        save_data: 存档数据

    Returns:
        推荐的标签列表
    """
    tags = []

    # 根据任务推荐
    active_quests = save_data.get("active_quest_ids", [])
    if active_quests:
        tags.append("主线任务")

    completed_quests = save_data.get("completed_quest_ids", [])
    if completed_quests:
        tags.append("支线任务")

    # 根据等级推荐
    player_data = save_data.get("player", {})
    level = player_data.get("level", 1)
    if level <= 5:
        tags.append("低等级")
    elif level <= 10:
        tags.append("中等级")
    else:
        tags.append("高等级")

    # 根据金币推荐
    gold = player_data.get("gold", 0)
    if gold > 100:
        tags.append("资金充足")

    # 根据装备推荐
    equipped_weapon = player_data.get("equipped_weapon_id")
    equipped_armor = player_data.get("equipped_armor_id")
    if equipped_weapon or equipped_armor:
        tags.append("装备齐全")

    return tags
