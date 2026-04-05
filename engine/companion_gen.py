"""
队友生成：LLM JSON → Pydantic 校验；失败回退模板。
"""

from __future__ import annotations

from core.narrative_language import get_narrative_language, user_locale_tail
from engine.llm_client import LLMClient
from game.companion import CompanionBlueprint, fallback_companion_blueprint
from game.dynamic_npc import extract_json_object
from game.game_state import GameState
from story.world_config import get_world_lore


def parse_companion_blueprint(raw_llm: str) -> CompanionBlueprint | None:
    data = extract_json_object(raw_llm)
    if not data:
        return None
    try:
        return CompanionBlueprint.model_validate(data)
    except Exception:
        return None


def generate_companion_blueprint(llm: LLMClient, state: GameState) -> CompanionBlueprint:
    player = state.player
    pname = player.name if player else "旅人"
    prof = player.profession.value if player else "冒险者"

    if get_narrative_language() == "en":
        system = (
            "You are a medieval fantasy RPG companion generator. Output ONE valid JSON object only, no markdown.\n"
            "No modern tech, real nations, or internet slang.\n"
            "hidden_trait_type must be exactly one of: spy, coward, loyal_dog, ambitious, cursed.\n"
            "hidden_trait_clue: one line of daily dialogue that might give them away (quotes allowed)."
        )
        user = (
            f"World: {get_world_lore()}\n"
            f"Player: {pname} ({prof}).\n"
            "Generate one possible party member with fields:\n"
            "name, appearance, personality, join_condition, special_skill, "
            "hidden_trait_type, hidden_trait_clue\n"
            "join_condition must be short and concrete (e.g. pay a debt, forge papers)."
        )
    else:
        system = (
            "你是中世纪奇幻 RPG 的「队友生成器」。只输出一个合法 JSON 对象，不要 markdown，不要解释。\n"
            "禁止现代科技、现实国家与网络用语。\n"
            "hidden_trait_type 必须从以下之一选取（原样输出中文）："
            "间谍、懦夫、忠犬、野心家、被诅咒者。\n"
            "hidden_trait_clue 为一句日常可能露馅的台词（可含引号）。"
        )
        user = (
            f"世界观：{get_world_lore()}\n"
            f"玩家：{pname}（{prof}）。\n"
            "生成一名可能加入队伍的冒险者，字段：\n"
            "name, appearance, personality, join_condition, special_skill, "
            "hidden_trait_type, hidden_trait_clue\n"
            "join_condition 要简短具体（例如赎回当物、弄到假文书）。"
        )
    user = user + user_locale_tail()
    raw = llm.generate_text(user, system=system, temperature=0.82, max_tokens=900)
    return parse_companion_blueprint(raw) or fallback_companion_blueprint()
