"""
叙事语言：与 Streamlit session 同步，供所有 LLM 调用统一输出语种（中/英）。
"""

from __future__ import annotations

import re
from contextvars import ContextVar

ALLOWED_LANGUAGES = frozenset({"zh", "en"})

# 每个执行上下文独立语言，避免不同会话互相污染
_current_lang: ContextVar[str] = ContextVar("narrative_language", default="zh")


def set_narrative_language(code: str) -> None:
    _current_lang.set(code if code in ALLOWED_LANGUAGES else "zh")


def get_narrative_language() -> str:
    return _current_lang.get()


def language_label(code: str) -> str:
    return {"zh": "中文", "en": "English"}.get(code, code)


def pick_lang(zh_text: str, en_text: str) -> str:
    """按当前叙事语言返回对应文案。"""
    return en_text if get_narrative_language() == "en" else zh_text


def merged_system_prompt(system: str | None) -> str | None:
    """
    将「必须使用某语种」规则并入 system；generate_text 在 system 非空时必调。
    """
    lang = get_narrative_language()
    if lang == "en":
        rule = (
            "【Output language】All narrated content, dialogue, and descriptions you produce must be in English. "
            "Do not use Chinese for player-visible text unless it is a proper name or short quoted epithet."
        )
    else:
        rule = (
            "【语言-中文】你必须使用简体中文撰写所有面向玩家的对白、叙述与描写。\n"
            "禁止：英文单词/缩写、拉丁字母拼词（如 ripples、vibe、NPC、OK、quest）；"
            "若写等级/任务须用「等级」「任务」等中文，勿夹英文字。\n"
            "概念一律用中文表达（例：涟漪、月色、气息）。\n"
            "除「已有汉字音译的人名、地名」外不要夹带西文；不要写中日混排的英文从句。"
        )
    base = (system or "").strip()
    if not base:
        return rule
    return f"{base}\n\n{rule}"


def user_locale_tail() -> str:
    """追加到 user prompt 末尾，强化语种（与 merged_system 双保险）。"""
    if get_narrative_language() == "en":
        return "\n\n(Write the entire response in English.)"
    return (
        "\n\n（请全文使用简体中文，不得出现英文单词或拉丁字母拼写；"
        "不要用 ripples、moonlight、vibe 等英文，应写「涟漪」「月色」「气氛」。）"
    )


def offline_llm_fallback() -> str:
    """LLMClient 离线占位。"""
    if get_narrative_language() == "en":
        return (
            "(Offline) Mist drifts between the trees. Distant echoes answer your steps. "
            "You steady your breath—the next choice may bring the truth closer."
        )
    return (
        "（离线模式）雾气在林间缓缓流动，远处传来隐约回响。"
        "你稳住呼吸，继续观察周遭——真相或许就藏在下一个选择之后。"
    )


def scene_prompt_tail() -> str:
    """场景描写 user 段末尾指令。"""
    if get_narrative_language() == "en":
        return (
            "Write a 120–180 word immersive scene in English. No choices or summary; "
            "no modern internet slang; stay in medieval fantasy tone.\n"
            "Vary each time: rotate sensory focus (sound / light / smell / small object / brief NPC beat); "
            "do not open every paragraph with the same mist+well+moon+forest-edge formula."
            f"{user_locale_tail()}"
        )
    return (
        "请用中文写一段 120–180 字的沉浸式场景描写，第二人称「你」或中性旁观，不要给选项或总结。\n"
        "同一段里不要堆砌多种大景：若已写到井水月光，就不要再续写「森林边缘全村迷雾」等另一套宏大意象；"
        "装备只作点到为止的反应，勿用「我盔甲长剑油光闪烁」式口号化自夸。\n"
        "严格遵守上文【本轮焦点】的角度，避免与常见起手（老井映月、迷雾笼村、林缘即景）逐字复读。"
        f"{user_locale_tail()}"
    )


def scene_system_brief() -> str:
    if get_narrative_language() == "en":
        return (
            "You are a restrained medieval-fantasy narrator with vivid imagery. "
            "No modern memes or off-topic content."
        )
    return (
        "你是中世纪奇幻世界的叙事者，文风克制、具体而少陈词滥调。"
        "禁止现代网络用语；禁止为凑字数重复使用「森林边缘的村庄被迷雾笼罩、老井、月色幽暗」等同一组合拳。"
        "每次生成要在意象与句法上与上一段拉开差别（换细节、换感官、换切入点）。"
    )


def scene_variety_instruction(round_count: int) -> str:
    """依回合轮换描写焦点，减轻千篇一律的环境段。"""
    if get_narrative_language() == "en":
        lenses = (
            "【Lens】Sound & silence first; one clause for setting only.",
            "【Lens】Light, shadow, warmth or chill; avoid repeating fluff about mist every time.",
            "【Lens】Scent, dust, smoke, damp earth—pick one thread.",
            "【Lens】A tiny prop or ground detail (strap, nail, cracked tile); wide vista in ≤8 words.",
            "【Lens】A villager’s small gesture or an animal; setting stays in the background.",
            "【Lens】Weather edge (wind, drizzle) without reusing the same opening as prior beats.",
        )
    else:
        lenses = (
            "【本轮焦点】以「远近声响、脚步、寂静中的杂音」为主；远景只一笔，忌老井+月色定式开场。",
            "【本轮焦点】以「光线、阴影、冷暖」为主；少写「全村迷雾森林边」万能布景。",
            "【本轮焦点】以「气味：尘土、潮气、炊烟、雨」择一展开，勿叠床架屋。",
            "【本轮焦点】以一个极小的静物或地面痕迹（绳结、泥印、木栅裂缝）切入，大景不超过一句。",
            "【本轮焦点】以一个路人小动作或畜牲的动态带过环境，不要复述上段的比喻句。",
            "【本轮焦点】以天气边角（风、细雨、飘雪屑）切入；禁止与前几轮同一句式起头。",
        )
    return lenses[round_count % len(lenses)]


# 中文叙事里常见的英文渗漏 / 损坏词（如 ripples → ipples）
_ZH_LATIN_NOISE = re.compile(
    r"(?i)\b("
    r"ripples?|ipples|moonlights?|moonlight|"
    r"vibes?|silence|whispers?|shadows?|mists?|echoes?|"
    r"figures?|darkness|breezes?"
    r")\b",
)
# 仍为纯拉丁字母且长度≥3 的残片（不含数字）
_ZH_LATIN_RUN = re.compile(r"(?<![A-Za-z0-9À-ÿ])([A-Za-z]{3,})(?![A-Za-z0-9À-ÿ])")


def scrub_latin_leakage_zh(text: str) -> str:
    """
    移除中文模式下易出现的英文词与孤立拉丁片段；尽量不破壞汉字与标点。
    在 LLM 仍漏英文時作後處理，不能替代提示詞約束。
    """
    if not text or get_narrative_language() != "zh":
        return text
    # 先處理黏在漢字後的殘片（如「微风的ipples」無法用 \\b 匹配 ipples）
    t = re.sub(r"(?i)ipples", "涟漪", text)
    t = re.sub(r"(?i)moonlight", "月色", t)
    t = _ZH_LATIN_NOISE.sub("", t)
    t = _ZH_LATIN_RUN.sub("", t)
    t = re.sub(r"[ \t\u3000]{2,}", " ", t)
    t = re.sub(r" *\n *", "\n", t)
    t = re.sub(r"\(\s*\)", "", t)
    return t.strip()
