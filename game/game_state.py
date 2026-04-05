"""
游戏状态：场景、时间、回合、任务、关键选择、标签；JSON 存档。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from core.exceptions import SaveLoadError
from game.constants import ROUNDS_PER_TIME_PERIOD, TIME_ORDER
from game.domain_version import GAME_STATE_DOMAIN_VERSION
from game.save_migrations import CURRENT_SAVE_SCHEMA, migrate_save_dict
from game.player import Player
from game.quest_system import QuestBook
from story.manifest import STORY_ASSET_VERSION


@dataclass
class GameState:
    """全局游戏状态（可序列化）。"""

    current_scene_id: str = "village_square"
    time_period_index: int = 0
    round_count: int = 0
    unlocked_scenes: set[str] = field(default_factory=set)
    completed_quest_ids: set[str] = field(default_factory=set)
    active_quest_ids: set[str] = field(default_factory=set)
    key_choices: list[str] = field(default_factory=list)
    tags: set[str] = field(default_factory=set)
    npc_mood: dict[str, str] = field(default_factory=dict)
    dynamic_npcs: list[dict[str, Any]] = field(default_factory=list)
    active_dynamic_npc_id: str | None = None
    companions: list[dict[str, Any]] = field(default_factory=list)
    pending_companion_offer: dict[str, Any] | None = None
    companion_fate_log: list[dict[str, Any]] = field(default_factory=list)
    flavor_log: list[dict[str, Any]] = field(default_factory=list)
    world_flags: dict[str, Any] = field(default_factory=dict)
    world_evolution: list[str] = field(default_factory=list)
    stat_counters: dict[str, int] = field(default_factory=dict)
    pending_gift_box: bool = False
    meta_break_budget: int = 3
    narrative_achievement_ids: list[str] = field(default_factory=list)
    newspaper_issue: int = 0
    game_state_domain_version: int = GAME_STATE_DOMAIN_VERSION
    game_log: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    player: Player | None = None
    quests: QuestBook = field(default_factory=QuestBook)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow().isoformat() + "Z"

    def time_label(self) -> str:
        return TIME_ORDER[self.time_period_index % len(TIME_ORDER)]

    def advance_round(self) -> None:
        """推进一回合并可能切换时间段。"""
        self.round_count += 1
        if self.round_count % ROUNDS_PER_TIME_PERIOD == 0:
            self.time_period_index = (self.time_period_index + 1) % len(TIME_ORDER)
        self.touch()

    def add_log(self, line: str) -> None:
        self.game_log.append(line)
        if len(self.game_log) > 200:
            self.game_log = self.game_log[-200:]
        self.touch()

    def add_key_choice(self, text: str) -> None:
        self.key_choices.append(text[:500])
        self.touch()

    def add_tag(self, tag: str) -> None:
        self.tags.add(tag[:64])
        self.touch()

    def unlock_scene(self, scene_id: str) -> None:
        self.unlocked_scenes.add(scene_id)
        self.touch()

    def to_dict(self) -> dict[str, Any]:
        if self.player is None:
            raise SaveLoadError("玩家未初始化，无法序列化。")
        return {
            "schema_version": CURRENT_SAVE_SCHEMA,
            "story_asset_version": STORY_ASSET_VERSION,
            "current_scene_id": self.current_scene_id,
            "time_period_index": self.time_period_index,
            "round_count": self.round_count,
            "unlocked_scenes": sorted(self.unlocked_scenes),
            "completed_quest_ids": sorted(self.completed_quest_ids),
            "active_quest_ids": sorted(self.active_quest_ids),
            "key_choices": list(self.key_choices),
            "tags": sorted(self.tags),
            "npc_mood": dict(self.npc_mood),
            "dynamic_npcs": list(self.dynamic_npcs),
            "active_dynamic_npc_id": self.active_dynamic_npc_id,
            "companions": list(self.companions),
            "pending_companion_offer": self.pending_companion_offer,
            "companion_fate_log": list(self.companion_fate_log),
            "flavor_log": list(self.flavor_log),
            "world_flags": dict(self.world_flags),
            "world_evolution": list(self.world_evolution),
            "stat_counters": dict(self.stat_counters),
            "pending_gift_box": self.pending_gift_box,
            "meta_break_budget": self.meta_break_budget,
            "narrative_achievement_ids": list(self.narrative_achievement_ids),
            "newspaper_issue": self.newspaper_issue,
            "game_state_domain_version": self.game_state_domain_version,
            "game_log": list(self.game_log),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "player": self.player.to_dict(),
            "quests": self.quests.to_dict(),
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "GameState":
        data = migrate_save_dict(dict(data))
        gs = GameState(
            current_scene_id=data.get("current_scene_id", "village_square"),
            time_period_index=int(data.get("time_period_index", 0)),
            round_count=int(data.get("round_count", 0)),
            unlocked_scenes=set(data.get("unlocked_scenes", [])),
            completed_quest_ids=set(data.get("completed_quest_ids", [])),
            active_quest_ids=set(data.get("active_quest_ids", [])),
            key_choices=list(data.get("key_choices", [])),
            tags=set(data.get("tags", [])),
            npc_mood=dict(data.get("npc_mood", {})),
            dynamic_npcs=list(data.get("dynamic_npcs", [])),
            active_dynamic_npc_id=data.get("active_dynamic_npc_id"),
            companions=list(data.get("companions", [])),
            pending_companion_offer=data.get("pending_companion_offer"),
            companion_fate_log=list(data.get("companion_fate_log", [])),
            flavor_log=list(data.get("flavor_log", [])),
            world_flags=dict(data.get("world_flags", {})),
            world_evolution=list(data.get("world_evolution", [])),
            stat_counters=dict(data.get("stat_counters", {})),
            pending_gift_box=bool(data.get("pending_gift_box", False)),
            meta_break_budget=int(data.get("meta_break_budget", 3)),
            narrative_achievement_ids=list(data.get("narrative_achievement_ids", [])),
            newspaper_issue=int(data.get("newspaper_issue", 0)),
            game_state_domain_version=int(
                data.get("game_state_domain_version", GAME_STATE_DOMAIN_VERSION)
            ),
            game_log=list(data.get("game_log", [])),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat() + "Z"),
            player=Player.from_dict(data["player"]),
            quests=QuestBook.from_dict(data.get("quests", {})),
        )
        return gs

    def save(self, filepath: Path | str) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as e:
            raise SaveLoadError(str(e)) from e

    @staticmethod
    def load(filepath: Path | str) -> "GameState":
        path = Path(filepath)
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            return GameState.from_dict(data)
        except (OSError, json.JSONDecodeError, KeyError) as e:
            raise SaveLoadError(f"读取存档失败：{e}") from e
