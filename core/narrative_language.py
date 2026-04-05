"""
叙事语言：与 Streamlit session 同步，供所有 LLM 调用统一输出语种（中/英）。
"""

from __future__ import annotations

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
            "【语言】你必须使用简体中文撰写所有面向玩家的对白、叙述与描写；"
            "除专有名词外不要混用英文。"
        )
    base = (system or "").strip()
    if not base:
        return rule
    return f"{base}\n\n{rule}"


def user_locale_tail() -> str:
    """追加到 user prompt 末尾，强化语种（与 merged_system 双保险）。"""
    if get_narrative_language() == "en":
        return "\n\n(Write the entire response in English.)"
    return "\n\n（请全文使用简体中文。）"


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
            "no modern internet slang; stay in medieval fantasy tone."
        )
    return "请用中文写一段 120-180 字的沉浸式场景描写，不要给选项或总结。"


def scene_system_brief() -> str:
    if get_narrative_language() == "en":
        return (
            "You are a restrained medieval-fantasy narrator with vivid imagery. "
            "No modern memes or off-topic content."
        )
    return (
        "你是中世纪奇幻世界的叙事者，文风克制、有画面感。"
        "禁止出现现代网络用语或与奇幻村庄无关的内容。"
    )
