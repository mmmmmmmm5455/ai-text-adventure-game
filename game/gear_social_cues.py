"""
装备与身份在「社交场合」给 NPC 的提示：供对话模型做性格化反应，非数值战斗。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from game.repair_system import is_broken

if TYPE_CHECKING:
    from game.player import Player


def gear_public_impression(player: "Player") -> str:
    """
    一句话概括「旁人看你装备」的印象，写入日志与 LLM。
    """
    w = player.equipped_weapon_id
    a = player.equipped_armor_id
    w_item = next((x for x in player.inventory.items if x.item_id == w), None)
    a_item = next((x for x in player.inventory.items if x.item_id == a), None)
    if w_item and is_broken(w_item):
        w = None
    if a_item and is_broken(a_item):
        a = None
    bits: list[str] = []
    if w == "rusty_sword":
        bits.append("佩一把生锈短剑，像刚出门的新手冒险者")
    elif w is None:
        bits.append("未显见武器，像平民或隐藏锋芒的旅人")
    else:
        bits.append("带着像样的武器，不像完全外行")
    if a == "leather_armor":
        bits.append("身着皮甲，略有准备")
    elif a:
        bits.append("有防具护身")
    else:
        bits.append("防具不显，衣着平常")
    return "；".join(bits) + "。"


def gear_trust_signal_level(player: "Player") -> int:
    """
    粗略 1～5：越高越「看起来可靠/体面」，供长者等调整信任语气。
    """
    score = 1
    w = player.equipped_weapon_id
    a = player.equipped_armor_id
    w_item = next((x for x in player.inventory.items if x.item_id == w), None)
    a_item = next((x for x in player.inventory.items if x.item_id == a), None)
    if w_item and is_broken(w_item):
        w = None
    if a_item and is_broken(a_item):
        a = None
    if w and w != "rusty_sword":
        score += 2
    elif w == "rusty_sword":
        score += 1
    if a:
        score += 1
    if player.level >= 3:
        score += 1
    return min(5, max(1, score))


def npc_gear_behavior_cue(npc_id: str, player: "Player") -> str:
    """
    按 NPC 性格输出「导演说明」，约束模型如何结合装备反应。
    """
    imp = gear_public_impression(player)
    trust = gear_trust_signal_level(player)

    if npc_id == "elder":
        return (
            f"【对装备反应】旁人印象：{imp} "
            "你是长者：无论对方装备新旧都要耐心、庄重，不嘲笑新手。"
            f"若对方看起来可靠（信任信号约 {trust}/5，越高越体面），"
            "语气中可多一分托付与认真；若像新手，则以勉励、叮嘱为主，仍给任务线索。"
        )
    if npc_id == "merchant":
        return (
            f"【对装备反应】旁人印象：{imp} "
            "你是商人：永远热情招呼，像欢迎老主顾。"
            "装备体面则顺势推荐「新到的紧俏货、稍贵但管用」；若像新手，推荐实惠入门货、修补与药水，"
            "话里带点推销趣味但不要令人厌烦。"
        )
    if npc_id == "guard":
        return (
            f"【对装备反应】旁人印象：{imp} "
            "你是守卫：戒心重。装备寒酸可能多盘问两句；装备整齐则稍收敛敌意，但仍保持审视。"
        )
    if npc_id == "innkeeper":
        return (
            f"【对装备反应】旁人印象：{imp} "
            "你是旅店老板：好客八卦。从装束猜旅人故事，装备好夸一句「像见过世面」，"
            "新手则关心是否第一次进林、要不要热汤。"
        )
    if npc_id == "miner":
        return (
            f"【对装备反应】旁人印象：{imp} "
            "你是矿工：务实直爽。看武器防具只评「能不能保命」，少废话多实在。"
        )
    if npc_id == "hermit":
        return (
            f"【对装备反应】旁人印象：{imp} "
            "你是隐士：冷淡。浮华装备引你不屑，朴素或陈旧你反而略多一句提醒「林里不认花哨」。"
        )
    return f"【对装备反应】旁人印象：{imp} 请结合你的身份自然评价对方的装束，勿编造其背包物品。"
