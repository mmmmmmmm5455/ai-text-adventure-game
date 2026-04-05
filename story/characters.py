"""
NPC 定义：性格、背景、对话主题关键词。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NPCProfile:
    npc_id: str
    name: str
    role: str
    personality: str
    background: str
    topics: tuple[str, ...]
    # 语气偏敌视、易被挑衅；对话提示里会加强冲突感
    hostile: bool = False
    # 威慑检定：玩家 (力量+魅力+1~8) 需 ≥ 此值才可能勒索到金币
    intimidate_resistance: int = 12
    # 单次威慑成功时金币上限（实际随机）
    max_intimidate_payout: int = 22
    # 1–10：性格上是否愿意在对话里给「小额」施舍/打赏（仍受系统概率与上限约束）
    generosity: int = 5


NPCS: dict[str, NPCProfile] = {
    "elder": NPCProfile(
        npc_id="elder",
        name="长者艾德里安",
        role="村庄长者",
        personality="沉稳、忧虑、愿意托付重任",
        background="见证过多次灾厄，相信预言与集体记忆。",
        topics=("森林异象", "村庄历史", "封印"),
        hostile=False,
        intimidate_resistance=20,
        max_intimidate_payout=8,
        generosity=6,
    ),
    "merchant": NPCProfile(
        npc_id="merchant",
        name="商人莉娜",
        role="行商",
        personality="精明、健谈、重利也重人情",
        background="商队在森林边失踪过货物，对迷雾心存忌惮。",
        topics=("贸易路线", "失踪货物", "情报"),
        hostile=False,
        intimidate_resistance=17,
        max_intimidate_payout=35,
        generosity=7,
    ),
    "hermit": NPCProfile(
        npc_id="hermit",
        name="隐士卡西姆",
        role="隐修者",
        personality="孤僻、洞察、说话绕弯",
        background="曾深入洞穴研究符文，知晓部分真相。",
        topics=("符文", "洞穴", "内心试炼"),
        hostile=True,
        intimidate_resistance=15,
        max_intimidate_payout=15,
        generosity=3,
    ),
    "miner": NPCProfile(
        npc_id="miner",
        name="矿工布罗克",
        role="矿工",
        personality="豪爽、疲惫、务实",
        background="在山脉与遗迹间往返，弄丢过工具，也见过怪异光影。",
        topics=("矿脉", "工具", "遗迹通道"),
        hostile=False,
        intimidate_resistance=13,
        max_intimidate_payout=18,
        generosity=6,
    ),
    "innkeeper": NPCProfile(
        npc_id="innkeeper",
        name="旅店老板玛莎",
        role="旅店老板",
        personality="热情、八卦、善于倾听",
        background="听过无数旅人的故事，能拼凑传闻。",
        topics=("旅人传闻", "补给", "休息"),
        hostile=False,
        intimidate_resistance=11,
        max_intimidate_payout=20,
        generosity=8,
    ),
    "guard": NPCProfile(
        npc_id="guard",
        name="守卫雷恩",
        role="村庄守卫",
        personality="警惕、强硬、对可疑外人不客气",
        background="负责巡逻广场与森林边缘，压力巨大，见过浑水摸鱼的人。",
        topics=("巡逻", "治安", "武器"),
        hostile=True,
        intimidate_resistance=18,
        max_intimidate_payout=12,
        generosity=3,
    ),
}


def npc_for_scene(scene_id: str) -> list[str]:
    """返回某场景默认可对话的 NPC id 列表。"""
    mapping: dict[str, tuple[str, ...]] = {
        "village_square": ("elder", "merchant", "guard"),
        "misty_forest": ("hermit",),
        "ancient_mountains": ("miner",),
        "mountain_foot": ("merchant",),
        "tavern": ("innkeeper", "merchant"),
        "mysterious_cave": ("hermit", "miner"),
        "underground_ruins": ("hermit",),
    }
    return list(mapping.get(scene_id, ()))
