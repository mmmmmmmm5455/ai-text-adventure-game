"""
结局类型与判定逻辑（不依赖 LLM，保证可离线演示）。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.i18n import t
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
            t("ending.title.tragedy"),
            t("ending.summary.tragedy"),
        )
    if main_done and "hero_path" in tags:
        return EndingInfo(
            EndingId.HERO,
            t("ending.title.hero"),
            t("ending.summary.hero"),
        )
    if "hermit_path" in tags:
        return EndingInfo(
            EndingId.HERMIT,
            t("ending.title.hermit"),
            t("ending.summary.hermit"),
        )
    if state.player and state.player.gold >= 200 and "wealth_focus" in tags:
        return EndingInfo(
            EndingId.MERCHANT,
            t("ending.title.merchant"),
            t("ending.summary.merchant"),
        )
    if main_done:
        return EndingInfo(
            EndingId.TRAVEL,
            t("ending.title.travel"),
            t("ending.summary.travel_main_done"),
        )
    return EndingInfo(
        EndingId.TRAVEL,
        t("ending.title.travel"),
        t("ending.summary.travel_default"),
    )
