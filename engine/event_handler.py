"""
随机/条件事件：根据场景与回合触发简短叙事或状态影响。
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from core.narrative_language import get_narrative_language
from game.game_state import GameState


@dataclass
class GameEvent:
    message: str
    gold_delta: int = 0
    xp_delta: int = 0
    hp_delta: int = 0


def maybe_trigger_event(state: GameState) -> GameEvent | None:
    """较低概率触发一个简单事件。"""
    if random.random() > 0.12:
        return None
    scene = state.current_scene_id
    pool: list[GameEvent]
    en = get_narrative_language() == "en"
    if scene == "misty_forest":
        pool = [
            GameEvent(
                "A chill brushes the branches; you feel briefly dizzy (then steady).",
                hp_delta=-3,
            )
            if en
            else GameEvent("一缕冷风掠过树梢，你感到轻微的眩晕（但很快恢复）。", hp_delta=-3),
            GameEvent("You find a few coins under the moss.", gold_delta=5)
            if en
            else GameEvent("你在苔藓下发现几枚铜币。", gold_delta=5),
        ]
    elif scene == "mysterious_cave":
        pool = [
            GameEvent("Drip echoes from the deep; the sound seems to whisper.", xp_delta=5)
            if en
            else GameEvent("洞穴深处传来水滴声，回音像在低语。", xp_delta=5),
            GameEvent(
                "A loose stone at your foot hides a small pouch of silver.",
                gold_delta=15,
            )
            if en
            else GameEvent("你脚边有一块松动的石头，下面藏着小袋银币。", gold_delta=15),
        ]
    else:
        pool = [
            GameEvent("Distant bells unfold, marking the passage of time.")
            if en
            else GameEvent("远处钟声缓缓荡开，提醒着时间的流逝。"),
            GameEvent("A crow lifts from the eaves and vanishes into the mist.")
            if en
            else GameEvent("一只乌鸦从屋檐飞起，消失在薄雾中。"),
        ]
    ev = random.choice(pool)
    if state.player:
        state.player.gold = max(0, state.player.gold + ev.gold_delta)
        for msg in state.player.gain_xp(ev.xp_delta):
            state.add_log(msg)
        if ev.hp_delta < 0:
            state.player.take_damage(-ev.hp_delta)
            if state.player.hp > 0 and state.player.hp * 5 <= state.player.max_hp:
                state.add_tag("brink_of_death")
        elif ev.hp_delta > 0:
            state.player.heal(ev.hp_delta)
    return ev
