"""
调用 LLM 生成动态广场路人 JSON；失败由上层回退模板。
"""

from __future__ import annotations

from typing import Any

from core.narrative_language import get_narrative_language, user_locale_tail
from engine.llm_client import LLMClient
from game.dynamic_npc import Tier
from game.game_state import GameState
from story.world_config import get_world_lore


def _existing_summary(npcs: list[dict[str, Any]]) -> str:
    if not npcs:
        return "（当前没有其它在场路人。）"
    lines = []
    for n in npcs[-3:]:
        lines.append(f"- {n.get('name','?')}：{n.get('request','')[:80]}")
    return "\n".join(lines)


def generate_dynamic_npc_json(
    llm: LLMClient,
    state: GameState,
    tier: Tier,
) -> str:
    """
    返回模型原始文本（应含 JSON）；由 game.dynamic_npc.parse_blueprint 解析。
    """
    player = state.player
    pname = player.name if player else "旅人"
    prof = player.profession.value if player else "冒险者"
    vis = player.visible_equipment_for_npc() if player else ""

    tier_hint = {
        "common": "奖励偏金币或消耗品线索，格局小，生活化。",
        "rare": "可出现装备、稍多金币或关键支线口吻的线索。",
        "epic": "可指向隐藏异闻或神秘线索，但不要破坏主线设定；语气更玄。",
    }[tier]

    tier_hint_en = {
        "common": "Small-stakes rewards: gold or consumable-style clues.",
        "rare": "May include gear, more gold, or subplot-flavored clues.",
        "epic": "May hint at hidden lore; do not break main plot; more mystical tone.",
    }[tier]

    if get_narrative_language() == "en":
        system = (
            "You improvise one square NPC for a medieval fantasy village. Output valid JSON only, no markdown fences.\n"
            "Setting: village by a misty forest; no modern tech, memes, or real brands.\n"
            "All keys required; reward_type must be one of clue, gold, item, stat, hidden_plot.\n"
            "reward_value is a suggested integer (game will rebalance); objective_count is 1–5 progress steps.\n"
            "If linked_npc_name matches someone in the list, weave a light story hook; else null.\n"
            "hidden_trigger: none | rusty_weapon | has_armor.\n"
            "opening: 2–3 lines of dialogue + micro-action in English, matching personality."
        )
        user = (
            f"World summary: {get_world_lore()}\n"
            f"Tier: {tier}. {tier_hint_en}\n"
            f"Player: {pname} ({prof}), visible gear: {vis}\n"
            f"Already present:\n{_existing_summary(list(state.dynamic_npcs))}\n\n"
            "Generate one JSON object with keys:\n"
            "name, appearance, personality, request, opening, reward_type, reward_value, "
            "objective_count, reward_description, hidden_trigger, linked_npc_name\n"
            "All narrative string values must be English."
        )
    else:
        system = (
            "你是中世纪奇幻小镇「广场」上的即兴剧编剧，只输出合法 JSON，不要 markdown 代码块，不要多余解释。\n"
            "世界观约束：中世纪奇幻村庄与迷雾森林，禁止现代科技、网络梗、现实品牌。\n"
            "字段必须全部存在；reward_type 只能是 clue、gold、item、stat、hidden_plot 之一。\n"
            "reward_value 为建议整数（系统会再平衡）；objective_count 为完成任务需要的「进度次数」1～5。\n"
            "若下列「已在场路人」中有可衔接的名字，可把 linked_npc_name 设为其中一人的 name，写一段能接上的剧情钩子；否则填 null。\n"
            "hidden_trigger：none | rusty_weapon（若玩家佩生锈短剑可触发隐藏加成）| has_armor（若穿护甲）。\n"
            "opening：2～3 句中文台词+微动作，符合 personality。"
        )
        user = (
            f"世界观摘要：{get_world_lore()}\n"
            f"奖励档位：{tier}。{tier_hint}\n"
            f"玩家：{pname}（{prof}），外露装备摘要：{vis}\n"
            f"已在场路人：\n{_existing_summary(list(state.dynamic_npcs))}\n\n"
            "请生成一名广场路人，严格输出一个 JSON 对象，键为：\n"
            "name, appearance, personality, request, opening, reward_type, reward_value, "
            "objective_count, reward_description, hidden_trigger, linked_npc_name\n"
            "示例 reward_description：「一小袋磨亮的铜币与低声叮嘱」。"
        )

    user = user + user_locale_tail()
    return llm.generate_text(user, system=system, temperature=0.82, max_tokens=900)
