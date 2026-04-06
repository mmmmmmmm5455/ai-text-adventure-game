"""叙事语言核心逻辑。"""

from __future__ import annotations

from core.narrative_language import (
    merged_system_prompt,
    offline_llm_fallback,
    scrub_latin_leakage_zh,
    set_narrative_language,
    user_locale_tail,
)


def teardown_function() -> None:
    set_narrative_language("zh")


def test_merged_system_defaults_zh() -> None:
    set_narrative_language("zh")
    m = merged_system_prompt("你是叙事者。")
    assert m
    assert "简体中文" in m
    assert "叙事者" in m


def test_merged_system_en() -> None:
    set_narrative_language("en")
    m = merged_system_prompt("You are a narrator.")
    assert m
    assert "English" in m


def test_offline_fallback_bilingual() -> None:
    set_narrative_language("zh")
    assert "离线" in offline_llm_fallback()
    set_narrative_language("en")
    assert "Offline" in offline_llm_fallback()


def test_user_locale_tail() -> None:
    set_narrative_language("zh")
    assert "中文" in user_locale_tail()
    set_narrative_language("en")
    assert "English" in user_locale_tail()


def test_scrub_latin_leakage_zh() -> None:
    set_narrative_language("zh")
    raw = "水面荡漾着微风的ipples，moonlight 洒下，仍有 silence 残留。"
    out = scrub_latin_leakage_zh(raw)
    assert "ipples" not in out
    assert "moonlight" not in out.lower()
    assert "silence" not in out.lower()
    assert "水面" in out


def test_scrub_noop_when_en() -> None:
    set_narrative_language("en")
    s = "The moonlight ripples on the well."
    assert scrub_latin_leakage_zh(s) == s
