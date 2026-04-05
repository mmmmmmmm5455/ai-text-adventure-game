"""
队友相关叙事：营地私语、结局背叛/忠诚描写（LLM + 降级）。
"""

from __future__ import annotations

from core.narrative_language import get_narrative_language
from engine.llm_client import LLMClient
from game.companion import TRAIT_LABEL_ZH, CompanionFateResult
from loguru import logger
from story.endings import EndingInfo


def generate_probe_banter(llm: LLMClient, companion: dict) -> str:
    """试探对话：短句，不直接点破身份。"""
    system = (
        "你是奇幻 RPG 对话写手。只输出 1～2 句角色台词（可带简短动作），"
        "玩家正在试探队友；回答要含糊、可解读为忠诚也可解读为隐瞒。"
        "禁止现代科技。"
    )
    user = (
        f"队友：{companion.get('name','')}，性格：{companion.get('personality','')}\n"
        "玩家随口试探其来历与立场，请写队友的回应。"
    )
    try:
        t = llm.generate_text(user, system=system, temperature=0.8, max_tokens=180)
        if t.strip():
            return t.strip()
    except Exception as e:
        logger.warning("队友试探对话生成失败，使用降级文案：{}", e)
    if get_narrative_language() == "en":
        return (
            f"{companion.get('name', 'They')} smiles faintly: "
            "“Pry too deep, and neither of us wins. Trust me—follow.”"
        )
    return (
        f"{companion.get('name','对方')}垂眼笑了笑："
        "“问得太细，对彼此都没好处。你信我，就跟上。”"
    )


def generate_camp_whisper(llm: LLMClient, companion: dict) -> str:
    """休息时偶发的梦话/异样举动。"""
    t = companion.get("hidden_trait", {}).get("type", "?")
    zh = TRAIT_LABEL_ZH.get(t, t)
    trait_hint = zh if get_narrative_language() != "en" else str(t)
    system = (
        "你是中世纪奇幻叙事者，只输出 1～2 句（可含角色台词），"
        "描写队友在篝火边的梦话或细微异常，不要剧透直说身份，但要让人心里发毛。"
        "禁止现代科技。"
    )
    user = (
        f"队友：{companion.get('name','')}，性格：{companion.get('personality','')}\n"
        f"隐藏类型（你心里有数，不要明说）：{trait_hint}\n"
        "写篝火边的一幕。"
    )
    try:
        text = llm.generate_text(user, system=system, temperature=0.85, max_tokens=220)
        if text.strip():
            return text.strip()
    except Exception as e:
        logger.warning("营地私语生成失败，使用降级文案：{}", e)
    if get_narrative_language() == "en":
        return (
            f"{companion.get('name', 'Your ally')} clenches a fist in sleep, "
            "mutters words you cannot parse, then falls silent."
        )
    return (
        f"{companion.get('name','队友')}在睡梦中攥紧了拳头，"
        "低声嘟囔了几句你听不懂的词句，又骤然安静。"
    )


def generate_companion_fate_narrative(
    llm: LLMClient,
    companion: dict,
    ending: EndingInfo,
    fate: CompanionFateResult,
) -> str:
    """结局时队友收场；要求呼应 hidden_trait_clue。"""
    t = companion.get("hidden_trait", {}).get("type", "")
    zh = TRAIT_LABEL_ZH.get(t, t)
    trait_line = zh if get_narrative_language() != "en" else str(t)
    clue = companion.get("hidden_trait_clue", "")
    loyalty = int(companion.get("loyalty_score", 50))
    if fate.twist_loyal_subversion:
        outcome = (
            "Loyalty twist (ambition yields, kneels and swears)"
            if get_narrative_language() == "en"
            else "反转效忠（野心收敛，跪拜宣誓追随）"
        )
    elif fate.betrayed:
        outcome = "Betrayal or loss of control" if get_narrative_language() == "en" else "背叛或失控"
    else:
        outcome = (
            "Steadfast or sacrificial loyalty"
            if get_narrative_language() == "en"
            else "坚守或牺牲式忠诚"
        )

    system = (
        "你是奇幻小说作者，写一段不超过 220 字的戏剧性收场，包含台词。\n"
        "若判定为背叛，必须合理解释此前对玩家的帮助可能是伪装或各取所需；"
        "禁止现代科技。\n"
        "必须自然呼应玩家曾听过的那句隐藏线索台词的精神（可化用，不必原句照抄）。"
    )
    tail = (
        "Write the companion's actions and key lines at the finale."
        if get_narrative_language() == "en"
        else "请写队友在终局时刻的行为与关键台词。"
    )
    user = (
        f"结局：{ending.title} — {ending.summary}\n"
        f"队友：{companion.get('name','')}\n"
        f"隐藏类型：{trait_line}\n"
        f"忠诚度：{loyalty}/100\n"
        f"线索台词：{clue}\n"
        f"最终判定：{outcome}\n"
        f"{tail}"
    )
    try:
        text = llm.generate_text(user, system=system, temperature=0.82, max_tokens=650)
        if text.strip():
            return text.strip()
    except Exception as e:
        logger.warning("队友终局叙事生成失败，使用降级文案：{}", e)
    if get_narrative_language() == "en":
        if fate.twist_loyal_subversion:
            return (
                f"{companion.get('name','')} drops to one knee: "
                "“I meant to replace you—yet I cannot walk your road. This blade is yours.”"
            )
        if fate.betrayed:
            return (
                f"{companion.get('name','')} fades into shadow: "
                "“You thought that help was love? It was only what the board required.”"
            )
        return (
            f"{companion.get('name','')} steps beside you: "
            "“Go—I’ll cover you. Don’t look back.”"
        )
    if fate.twist_loyal_subversion:
        return (
            f"{companion.get('name','')}单膝跪地，额头触地："
            "“我曾想取代你……可你走的路，我终究跟不上。这柄剑，从此只向你。”"
        )
    if fate.betrayed:
        return (
            f"{companion.get('name','')}退入阴影，声音冷下来："
            "“你以为那些相助是情义？不过是棋局里必要的棋子罢了。”"
        )
    return (
        f"{companion.get('name','')}挡在你身侧，轻声道："
        "“走——我断后。别回头。”"
    )
