"""
队友：隐藏倾向、忠诚度、结局背叛判定（数值由代码主导，模型负责叙事）。
"""

from __future__ import annotations

import random
import secrets
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from story.endings import EndingId, EndingInfo

HiddenTraitType = Literal["spy", "coward", "loyal_dog", "ambitious", "cursed"]

TRAIT_LABEL_ZH: dict[str, str] = {
    "spy": "间谍",
    "coward": "懦夫",
    "loyal_dog": "忠犬",
    "ambitious": "野心家",
    "cursed": "被诅咒者",
}

# 基础「叛变/失控」倾向（0~1），再由忠诚度与事件修正
TRAIT_BASE_BETRAY: dict[str, float] = {
    "spy": 0.55,
    "coward": 0.45,
    "loyal_dog": 0.05,
    "ambitious": 0.52,
    "cursed": 0.45,
}

JOIN_GOLD_COST = 20


def normalize_trait_type(raw: str) -> HiddenTraitType:
    s = (raw or "").strip().lower()
    mapping = {
        "间谍": "spy",
        "spy": "spy",
        "懦夫": "coward",
        "coward": "coward",
        "忠犬": "loyal_dog",
        "loyal_dog": "loyal_dog",
        "野心家": "ambitious",
        "ambitious": "ambitious",
        "被诅咒者": "cursed",
        "诅咒者": "cursed",
        "cursed": "cursed",
    }
    out = mapping.get(s) or mapping.get(raw.strip(), "coward")
    return out  # type: ignore[return-value]


class CompanionBlueprint(BaseModel):
    model_config = {"extra": "ignore"}

    name: str = Field(..., max_length=56)
    appearance: str = Field(default="", max_length=520)
    personality: str = Field(default="", max_length=280)
    join_condition: str = Field(default="", max_length=320)
    special_skill: str = Field(default="", max_length=200)
    hidden_trait_type: str = Field(default="coward", max_length=32)
    hidden_trait_clue: str = Field(default="", max_length=360)


def fallback_companion_blueprint() -> CompanionBlueprint:
    return CompanionBlueprint(
        name="沉默的佣兵·灰隼",
        appearance="披着洗旧的灰斗篷，指节有老茧，目光总在出口停留。",
        personality="话少、服从命令，但从不谈自己的过去。",
        join_condition="替他付清旅店的赊账（系统按金币结算）。",
        special_skill="警戒姿态（休息时更易察觉危险）。",
        hidden_trait_type="spy",
        hidden_trait_clue="“我习惯记住每条退路——这不是多疑，是职业。”",
    )


def companion_record_from_blueprint(bp: CompanionBlueprint, rng: random.Random | None = None) -> dict[str, Any]:
    r = rng or random
    trait = normalize_trait_type(bp.hidden_trait_type)
    hidden_value = round(r.uniform(0.15, 0.92), 3)
    curse_intensity: float | None = None
    if trait == "cursed":
        curse_intensity = round(r.uniform(0.3, 0.9), 3)
    cid = "c_" + secrets.token_hex(4)
    return {
        "companion_id": cid,
        "name": bp.name.strip()[:56],
        "avatar_desc": (bp.appearance or bp.name).strip()[:520],
        "personality": bp.personality.strip()[:280],
        "join_condition": bp.join_condition.strip()[:320],
        "special_skill": bp.special_skill.strip()[:200],
        "hidden_trait_clue": bp.hidden_trait_clue.strip()[:360],
        "hidden_trait": {
            "type": trait,
            "value": hidden_value,
            "is_betrayer": False,
            "curse_intensity": curse_intensity,
        },
        "loyalty_score": 50,
        "party_status": "inactive",
    }


def get_active_companion(state: Any) -> dict[str, Any] | None:
    for c in getattr(state, "companions", []) or []:
        if c.get("party_status") == "active":
            return c
    return None


def set_active_companion(state: Any, companion_id: str | None) -> None:
    for c in state.companions:
        c["party_status"] = "active" if c.get("companion_id") == companion_id else "inactive"
    state.touch()


@dataclass(frozen=True)
class CompanionFateResult:
    betrayed: bool
    twist_loyal_subversion: bool
    reason_code: str


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def resolve_companion_fate(
    state: Any,
    companion: dict[str, Any],
    ending: EndingInfo,
    rng: random.Random | None = None,
) -> CompanionFateResult:
    """
    结局时判定队友是否背叛/失控；野心家可有「反转效忠」小概率事件。
    """
    r = rng or random
    ht = companion.get("hidden_trait") or {}
    t: str = ht.get("type", "coward")
    if t not in TRAIT_BASE_BETRAY:
        t = "coward"
    loyalty = int(companion.get("loyalty_score", 50))
    loyalty = max(0, min(100, loyalty))
    hv = float(ht.get("value") or 0.5)
    hv = _clamp01(hv)

    base = TRAIT_BASE_BETRAY[t]
    loyalty_mod = max(0.0, (50 - loyalty) / 100.0) * 0.42
    intensity_mod = hv * 0.22

    final = base + loyalty_mod + intensity_mod
    if "companion_contract" in state.tags:
        final -= 0.2
    if "companion_revealed" in state.tags:
        final -= 0.12
    if "companion_true_sight" in state.tags:
        final -= 0.15

    # 野心家：远行/隐居式收场时更易反目
    if t == "ambitious":
        if ending.ending_id in (EndingId.TRAVEL, EndingId.HERMIT):
            final += 0.18
        if ending.ending_id == EndingId.MERCHANT:
            final -= 0.08

    # 被诅咒者：用诅咒强度与忠诚共同推高失控概率
    if t == "cursed":
        ci = float(ht.get("curse_intensity") or 0.55)
        final = ci * 0.55 + (100 - loyalty) / 100 * 0.35 + hv * 0.15

    final = _clamp01(final)

    betrayed = False
    twist = False
    reason = "default_roll"

    if t == "spy" and loyalty < 30:
        betrayed = True
        reason = "spy_loyalty_break"
    elif t == "loyal_dog":
        if "killed_companion_beloved" in state.tags:
            betrayed = r.random() < 0.88
            reason = "loyal_dog_broken_bond"
        else:
            betrayed = r.random() < 0.05
            reason = "loyal_dog_rare"
    elif t == "coward":
        if "brink_of_death" in state.tags and loyalty < 48:
            betrayed = r.random() < _clamp01(0.58 + (48 - loyalty) / 200)
            reason = "coward_fled_peril"
        else:
            betrayed = r.random() < final
            reason = "coward_default"
    elif t == "cursed":
        betrayed = r.random() < final
        reason = "curse_backlash"
    else:
        betrayed = r.random() < final
        reason = "ambitious_or_default"

    # 野心家反转：高忠诚时可能由叛意转为跪拜效忠式收场
    if t == "ambitious" and betrayed and loyalty >= 58 and r.random() < 0.22:
        twist = True
        betrayed = False
        reason = "ambitious_twist_sworn"

    companion.setdefault("hidden_trait", {})["is_betrayer"] = bool(betrayed)
    return CompanionFateResult(
        betrayed=bool(betrayed),
        twist_loyal_subversion=twist,
        reason_code=reason,
    )


def apply_loyalty_delta(companion: dict[str, Any], delta: int) -> None:
    v = int(companion.get("loyalty_score", 50)) + delta
    companion["loyalty_score"] = max(0, min(100, v))
