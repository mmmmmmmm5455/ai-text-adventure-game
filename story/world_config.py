"""
世界总配置：聚合场景、NPC、物品、任务，并提供初始化入口。
"""

from __future__ import annotations

from game.game_state import GameState
from game.quest_system import QuestBook
from story.quests import default_quests
from story.scenes import SCENES


WORLD_NAME = "宁静村庄"
WORLD_LORE = (
    "森林边缘的中世纪小村，近来迷雾森林出现异象，旅人与村民皆不安。"
    "你作为外来冒险者，将调查真相并在抉择中书写自己的结局。"
)


def register_default_quests(book: QuestBook) -> None:
    """将默认任务注册到任务簿。"""
    for q in default_quests():
        book.register(q)


def initial_unlocked() -> set[str]:
    """初始已解锁场景（演示版开放全部地点，便于体验）。"""
    from story.scenes import SCENES

    return set(SCENES.keys())


def new_game_state(player_name: str, profession_key: str) -> GameState:
    """创建新游戏状态并挂载玩家与任务。"""
    from game.player import Player, Profession

    prof = Profession(profession_key)
    player = Player.create(player_name, prof)
    gs = GameState()
    gs.player = player
    gs.unlocked_scenes = initial_unlocked()
    register_default_quests(gs.quests)
    for q in gs.quests.all_quests():
        gs.active_quest_ids.add(q.quest_id)
    gs.add_log(f"欢迎来到「{WORLD_NAME}」，{player.name}。")
    return gs
