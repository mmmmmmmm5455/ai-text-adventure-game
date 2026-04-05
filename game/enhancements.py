"""
AI 趣味增强：计数器、世界标记、风味事件日志（与 enhancement_engine 配合）。
"""

from __future__ import annotations

from typing import Any

MAX_FLAVOR_LOG = 80
MAX_WORLD_EVOLUTION = 14
MAX_META_BREAKS = 3


def record_flavor_event(state: Any, kind: str, text: str) -> None:
    log = getattr(state, "flavor_log", None)
    if log is None:
        return
    entry = {
        "kind": kind,
        "text": text.strip()[:2000],
        "round": int(getattr(state, "round_count", 0)),
        "scene": getattr(state, "current_scene_id", ""),
    }
    log.append(entry)
    state.flavor_log = log[-MAX_FLAVOR_LOG:]
    state.touch()


def bump_counter(state: Any, key: str, delta: int = 1) -> int:
    c = getattr(state, "stat_counters", None)
    if c is None:
        return 0
    c[key] = int(c.get(key, 0)) + delta
    state.stat_counters = c
    state.touch()
    return c[key]


def append_world_evolution(state: Any, line: str) -> None:
    evo = list(getattr(state, "world_evolution", []) or [])
    evo.append(line.strip()[:500])
    state.world_evolution = evo[-MAX_WORLD_EVOLUTION:]
    state.touch()


def set_world_flag(state: Any, key: str, value: Any) -> None:
    wf = dict(getattr(state, "world_flags", {}) or {})
    wf[key] = value
    state.world_flags = wf
    state.touch()


NARRATIVE_ACHIEVEMENTS = (
    ("search_5", "searches", 5, "寻踪者"),
    ("rest_10", "rests", 10, "篝火友人"),
    ("talk_8", "npc_talks", 8, "言语之交"),
    ("move_12", "moves", 12, "漫行者"),
)
