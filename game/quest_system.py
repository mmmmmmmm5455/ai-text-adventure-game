"""
任务系统：主线/支线、进度、奖励（金币与经验）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class QuestKind(str, Enum):
    MAIN = "主线"
    SIDE = "支线"


@dataclass
class Quest:
    """单个任务定义与运行时进度。"""

    quest_id: str
    name: str
    description: str
    objectives: list[str]
    kind: QuestKind = QuestKind.SIDE
    progress: int = 0
    completed: bool = False
    reward_gold: int = 0
    reward_xp: int = 0
    meta: dict[str, Any] = field(default_factory=dict)

    def advance(self, delta: int = 1) -> None:
        self.progress = max(0, self.progress + delta)
        if self.objectives and self.progress >= len(self.objectives):
            self.completed = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "quest_id": self.quest_id,
            "name": self.name,
            "description": self.description,
            "objectives": list(self.objectives),
            "kind": self.kind.value,
            "progress": self.progress,
            "completed": self.completed,
            "reward_gold": self.reward_gold,
            "reward_xp": self.reward_xp,
            "meta": self.meta,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Quest":
        return Quest(
            quest_id=data["quest_id"],
            name=data["name"],
            description=data["description"],
            objectives=list(data.get("objectives", [])),
            kind=QuestKind(data.get("kind", QuestKind.SIDE.value)),
            progress=int(data.get("progress", 0)),
            completed=bool(data.get("completed", False)),
            reward_gold=int(data.get("reward_gold", 0)),
            reward_xp=int(data.get("reward_xp", 0)),
            meta=dict(data.get("meta", {})),
        )


class QuestBook:
    """任务簿：登记、更新、领取奖励接口。"""

    def __init__(self) -> None:
        self._quests: dict[str, Quest] = {}

    def register(self, quest: Quest) -> None:
        self._quests[quest.quest_id] = quest

    def get(self, quest_id: str) -> Quest | None:
        return self._quests.get(quest_id)

    def remove(self, quest_id: str) -> None:
        self._quests.pop(quest_id, None)

    def all_quests(self) -> list[Quest]:
        return list(self._quests.values())

    def active_quests(self) -> list[Quest]:
        return [q for q in self._quests.values() if not q.completed]

    def completed_quests(self) -> list[Quest]:
        return [q for q in self._quests.values() if q.completed]

    def to_dict(self) -> dict[str, Any]:
        return {"quests": [q.to_dict() for q in self._quests.values()]}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "QuestBook":
        book = QuestBook()
        for row in data.get("quests", []):
            q = Quest.from_dict(row)
            book._quests[q.quest_id] = q
        return book
