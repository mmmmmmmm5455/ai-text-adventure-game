"""
世界总配置：聚合场景、NPC、物品、任务，并提供初始化入口。
"""

from __future__ import annotations

from core.i18n import t
from game.game_state import GameState
from game.quest_system import QuestBook
from story.quests import default_quests
from story.scenes import SCENES


def get_world_name() -> str:
    return t("world.name")


def get_world_lore() -> str:
    return t("world.lore")


def register_default_quests(book: QuestBook) -> None:
    """将默认任务注册到任务簿。"""
    for q in default_quests():
        book.register(q)


def initial_unlocked() -> set[str]:
    """初始已解锁场景（演示版开放全部地点，便于体验）。"""
    from story.scenes import SCENES

    return set(SCENES.keys())


def new_game_state(player_name: str, profession_key: str, gender: str = "未指定") -> GameState:
    """创建新游戏状态并挂载玩家与任务。"""
    from game.player import Player, Profession

    try:
        prof = Profession(profession_key)
    except ValueError as e:
        raise ValueError(
            f"無效職業：{profession_key!r}；請使用：{', '.join(p.value for p in Profession)}"
        ) from e
    player = Player.create(player_name, prof, gender)
    gs = GameState()
    gs.player = player
    gs.unlocked_scenes = initial_unlocked()
    register_default_quests(gs.quests)
    for q in gs.quests.all_quests():
        gs.active_quest_ids.add(q.quest_id)
    gs.add_log(t("world.log.welcome", world=get_world_name(), name=player.name))
    gs.add_log(t("world.log.identity", gender=player.gender))
    return gs
