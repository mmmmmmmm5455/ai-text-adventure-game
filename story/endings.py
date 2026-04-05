"""
结局类型与判定逻辑（不依赖 LLM，保证可离线演示）。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from game.game_state import GameState


class EndingId(str, Enum):
    HERO = "hero"
    HERMIT = "hermit"
    MERCHANT = "merchant"
    TRAVEL = "travel"
    TRAGEDY = "tragedy"


@dataclass(frozen=True)
class EndingInfo:
    ending_id: EndingId
    title: str
    summary: str


def decide_ending(state: GameState) -> EndingInfo:
    """
    根据标签、任务与关键选择决定结局。
    优先级：悲剧 > 英雄 > 隐居 > 富商 > 远行
    """
    tags = state.tags
    main_done = "main_complete" in tags or state.completed_quest_ids.intersection({"main_forest"})
    if "village_fallen" in tags or (not state.player or not state.player.is_alive()):
        return EndingInfo(
            EndingId.TRAGEDY,
            "悲剧结局",
            "村庄的灯火在雾中熄灭，你的故事以遗憾收场。",
        )
    if main_done and "hero_path" in tags:
        return EndingInfo(
            EndingId.HERO,
            "英雄结局",
            "你驱散了洞穴深处的阴影，村民在广场上为你欢呼。",
        )
    if "hermit_path" in tags:
        return EndingInfo(
            EndingId.HERMIT,
            "隐居结局",
            "你选择在森林深处结庐，把时间交给风声与书卷。",
        )
    if state.player and state.player.gold >= 200 and "wealth_focus" in tags:
        return EndingInfo(
            EndingId.MERCHANT,
            "富商结局",
            "财富在你手中累积，商路与契约成为你新的冒险。",
        )
    if main_done:
        return EndingInfo(
            EndingId.TRAVEL,
            "远行结局",
            "真相已明，你背起行囊，把宁静村庄留在身后，走向更广阔的世界。",
        )
    return EndingInfo(
        EndingId.TRAVEL,
        "远行结局",
        "旅程尚未写下终章，前路仍在你脚下延展。",
    )
