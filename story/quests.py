"""
默认任务定义（静态），由 world_config 注册到 QuestBook。
"""

from __future__ import annotations

from core.narrative_language import get_narrative_language
from game.quest_system import Quest, QuestKind


def default_quests() -> list[Quest]:
    if get_narrative_language() == "en":
        return [
            Quest(
                quest_id="main_forest",
                name="Investigate Forest Anomalies",
                description="Find the source of abnormal energy in the Misty Forest and protect the village.",
                objectives=["Enter Misty Forest", "Enter Mysterious Cave", "Reach Underground Ruins"],
                kind=QuestKind.MAIN,
                reward_gold=50,
                reward_xp=80,
            ),
            Quest(
                quest_id="side_merchant",
                name="Merchant's Cargo",
                description="Help Lina recover a missing crate near the forest edge.",
                objectives=["Search in Misty Forest", "Return cargo to merchant"],
                kind=QuestKind.SIDE,
                reward_gold=30,
                reward_xp=40,
            ),
            Quest(
                quest_id="side_elder_cat",
                name="Elder's Cat",
                description="A cat went missing near the square; it may be by the tavern back alley.",
                objectives=["Search near tavern", "Bring cat back to square"],
                kind=QuestKind.SIDE,
                reward_gold=10,
                reward_xp=25,
            ),
            Quest(
                quest_id="side_miner_tool",
                name="Miner's Tool Bag",
                description="Brock left his tool bag on the mountain foot path.",
                objectives=["Find tool bag at mountain foot", "Return it to miner"],
                kind=QuestKind.SIDE,
                reward_gold=20,
                reward_xp=30,
            ),
        ]
    return [
        Quest(
            quest_id="main_forest",
            name="调查森林异象",
            description="查明迷雾森林中异常能量的来源，并保护村庄。",
            objectives=["进入迷雾森林", "进入神秘洞穴", "抵达地下遗迹"],
            kind=QuestKind.MAIN,
            reward_gold=50,
            reward_xp=80,
        ),
        Quest(
            quest_id="side_merchant",
            name="商人的货物",
            description="帮莉娜在森林边缘找回一箱货物。",
            objectives=["在迷雾森林搜寻", "将货物交还商人"],
            kind=QuestKind.SIDE,
            reward_gold=30,
            reward_xp=40,
        ),
        Quest(
            quest_id="side_elder_cat",
            name="长者的猫",
            description="广场附近走失的猫，可能在旅店后巷。",
            objectives=["在旅店附近寻找", "把猫带回广场"],
            kind=QuestKind.SIDE,
            reward_gold=10,
            reward_xp=25,
        ),
        Quest(
            quest_id="side_miner_tool",
            name="矿工的工具袋",
            description="布罗克把工具袋落在山脚路径上。",
            objectives=["在山脚地带找回工具袋", "交还给矿工"],
            kind=QuestKind.SIDE,
            reward_gold=20,
            reward_xp=30,
        ),
    ]
