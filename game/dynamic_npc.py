"""
动态广场路人：JSON 校验、奖励档位、数值钳制、交付结算。
"""

from __future__ import annotations

import json
import random
import re
import secrets
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from game.game_state import GameState
from game.quest_system import Quest, QuestKind

MAX_DYNAMIC_NPCS = 3

# 与 AIDialogueEngine 配合：session.npc_id == f"{DYNAMIC_DIALOGUE_PREFIX}{record['id']}"
DYNAMIC_DIALOGUE_PREFIX = "dyn:"

RewardType = Literal["clue", "gold", "item", "stat", "hidden_plot"]
Tier = Literal["common", "rare", "epic"]


class DynamicNpcBlueprint(BaseModel):
    """模型输出经校验后的蓝图（数值仍由交付逻辑再钳制）。"""

    model_config = {"extra": "ignore"}

    name: str = Field(..., max_length=48)
    appearance: str = Field(..., max_length=520)
    personality: str = Field(..., max_length=200)
    request: str = Field(..., max_length=420)
    opening: str = Field(..., max_length=420)
    reward_type: str
    reward_value: int = Field(default=1, ge=1, le=99)
    objective_count: int = Field(default=1, ge=1, le=8)
    reward_description: str = Field(default="", max_length=320)
    hidden_trigger: str = Field(default="none")
    linked_npc_name: str | None = Field(default=None, max_length=48)

    @field_validator("reward_type")
    @classmethod
    def _rt(cls, v: str) -> str:
        allowed = {"clue", "gold", "item", "stat", "hidden_plot"}
        if v not in allowed:
            return "gold"
        return v

    @field_validator("hidden_trigger")
    @classmethod
    def _ht(cls, v: str) -> str:
        if v not in ("none", "rusty_weapon", "has_armor"):
            return "none"
        return v


def roll_reward_tier(rng: random.Random | None = None) -> Tier:
    """60% 普通 / 30% 稀有 / 10% 隐藏档（更高上限与隐藏剧情概率）。"""
    r = (rng or random).random()
    if r < 0.6:
        return "common"
    if r < 0.9:
        return "rare"
    return "epic"


def extract_json_object(text: str) -> dict[str, Any] | None:
    text = text.strip()
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group())
    except json.JSONDecodeError:
        return None


def parse_blueprint(raw_llm: str) -> DynamicNpcBlueprint | None:
    data = extract_json_object(raw_llm)
    if not data:
        return None
    try:
        return DynamicNpcBlueprint.model_validate(data)
    except Exception:
        return None


def fallback_blueprint(tier: Tier) -> DynamicNpcBlueprint:
    """解析失败时的预设路人。"""
    flavor = {
        "common": ("神色疲惫的挑夫", "粗布衣衫上沾着泥点，肩上空着扁担。"),
        "rare": ("裹着旧斗篷的行商", "眼神机警，怀里紧揣一只小布包。"),
        "epic": ("低声祈祷的老妇人", "念珠磨得发亮，似乎知道些不该说的传闻。"),
    }
    name, appear = flavor[tier]
    return DynamicNpcBlueprint(
        name=name,
        appearance=appear,
        personality="焦虑、话少",
        request="帮忙在广场边找回落在泥里的护身符（搜寻广场即可有进展）。",
        opening="“外乡人……你若肯帮忙，我会记住你的恩情。”",
        reward_type="gold",
        reward_value=10,
        objective_count=1,
        reward_description="几枚叮当响的铜币与一句诚心道谢。",
        hidden_trigger="none",
        linked_npc_name=None,
    )


def blueprint_to_record(bp: DynamicNpcBlueprint, tier: Tier) -> dict[str, Any]:
    rid = "dn_" + secrets.token_hex(4)
    return {
        "id": rid,
        "name": bp.name.strip()[:48],
        "appearance": bp.appearance.strip()[:520],
        "personality": bp.personality.strip()[:200],
        "request": bp.request.strip()[:420],
        "opening": bp.opening.strip()[:420],
        "reward_type": bp.reward_type,
        "reward_value": int(bp.reward_value),
        "objective_count": int(bp.objective_count),
        "progress": 0,
        "mood": 50,
        "status": "fresh",
        "interaction_phase": "opening",
        "tier": tier,
        "reward_flavor": (bp.reward_description or "").strip()[:320],
        "hidden_trigger": bp.hidden_trigger,
        "hidden_bonus_applied": False,
        "linked_npc_id": None,
        "linked_blurb": None,
        "linked_npc_name": (bp.linked_npc_name or "").strip()[:48] or None,
    }


def dynamic_dialogue_session_id(npc_record_id: str) -> str:
    """生成自由对话用的 npc_id（与静态 NPC 的 story key 不冲突）。"""
    return f"{DYNAMIC_DIALOGUE_PREFIX}{npc_record_id}"


def find_dynamic_npc_for_dialogue(gs: GameState, session_npc_id: str) -> dict[str, Any] | None:
    """由 DialogueSession.npc_id 解析当前仍存在的路人记录。"""
    if not session_npc_id.startswith(DYNAMIC_DIALOGUE_PREFIX):
        return None
    rid = session_npc_id[len(DYNAMIC_DIALOGUE_PREFIX) :]
    return next((n for n in gs.dynamic_npcs if n.get("id") == rid), None)


def dynamic_npc_quest_id(npc_id: str) -> str:
    return f"dyn_{npc_id}"


def register_dynamic_npc_quest(gs: GameState, npc: dict[str, Any]) -> None:
    """接受路人委托后写入任务簿，供侧边栏「进行中任务」显示。"""
    nid = str(npc.get("id") or "")
    if not nid:
        return
    qid = dynamic_npc_quest_id(nid)
    if gs.quests.get(qid):
        return
    n_obj = max(1, min(8, int(npc.get("objective_count", 1))))
    name = (npc.get("name") or "路人委托").strip()[:48]
    desc = (npc.get("request") or "").strip()[:500]
    objs = [f"在村庄广场搜寻（{i + 1}/{n_obj}）" for i in range(n_obj)]
    q = Quest(
        quest_id=qid,
        name=name,
        description=desc,
        objectives=objs,
        kind=QuestKind.SIDE,
        progress=0,
        completed=False,
        meta={"dynamic_npc_id": nid, "source": "dynamic_npc"},
    )
    gs.quests.register(q)
    gs.active_quest_ids.add(qid)


def sync_dynamic_quest_progress(gs: GameState, npc: dict[str, Any]) -> None:
    """广场搜寻推进路人进度时，同步任务簿上的进度数字。"""
    nid = str(npc.get("id") or "")
    if not nid or npc.get("status") != "active":
        return
    q = gs.quests.get(dynamic_npc_quest_id(nid))
    if not q or q.completed:
        return
    p = int(npc.get("progress", 0))
    cap = len(q.objectives)
    q.progress = max(0, min(p, cap))


def complete_dynamic_npc_quest(gs: GameState, npc_id: str) -> None:
    """交付成功后标记任务完成。"""
    qid = dynamic_npc_quest_id(npc_id)
    q = gs.quests.get(qid)
    if not q:
        return
    q.completed = True
    if q.objectives:
        q.progress = len(q.objectives)
    gs.completed_quest_ids.add(qid)
    gs.active_quest_ids.discard(qid)


def remove_dynamic_npc_quest(gs: GameState, npc_id: str) -> None:
    """路人被挤出队列等情况下移除对应任务条目。"""
    if not npc_id:
        return
    qid = dynamic_npc_quest_id(npc_id)
    gs.quests.remove(qid)
    gs.active_quest_ids.discard(qid)
    gs.completed_quest_ids.discard(qid)


def apply_link_to_existing(new_rec: dict[str, Any], existing: list[dict[str, Any]]) -> None:
    """若模型提供了 linked_npc_name，与已在场的路人建立弱关联。"""
    name_key = (new_rec.get("linked_npc_name") or "").strip()
    if not name_key:
        new_rec.pop("linked_npc_name", None)
        return
    for other in existing:
        if other.get("name") == name_key and other.get("id") != new_rec.get("id"):
            new_rec["linked_npc_id"] = other["id"]
            new_rec["linked_blurb"] = (
                f"你想起「{other['name']}」似乎与这事有关——"
                f"对方曾念叨的物件，竟与眼前人所说的呼应。"
            )
            note = f"有位「{new_rec['name']}」正在打听与你有关的下落。"
            other["linked_blurb"] = (other.get("linked_blurb") or "").strip()
            if not other["linked_blurb"]:
                other["linked_blurb"] = note
            new_rec.pop("linked_npc_name", None)
            return
    new_rec.pop("linked_npc_name", None)


def check_hidden_bonus(player_weapon: str | None, player_armor: str | None, trigger: str) -> bool:
    if trigger == "rusty_weapon" and player_weapon == "rusty_sword":
        return True
    if trigger == "has_armor" and bool(player_armor):
        return True
    return False


def clamp_gold_for_tier(base: int, tier: Tier, mood: int, hidden_bonus: bool) -> int:
    mood_f = 0.88 + (max(0, min(100, mood)) / 100) * 0.28
    caps = {"common": 22, "rare": 38, "epic": 55}
    g = int(max(3, base) * mood_f)
    if hidden_bonus:
        g += 12
    return min(caps[tier], max(4, g))


def deliver_dynamic_quest_rewards(
    rec: dict[str, Any],
    *,
    player_gold_delta,
    player_add_item,
    player_add_stat,
    memory_add,
    catalog_item,
) -> list[str]:
    """
    按类型发奖；返回日志行列表。
    catalog_item: callable(id) -> 可加入背包的物品对象（含 .name）。
    """
    lines: list[str] = []
    tier = rec.get("tier", "common")
    if tier not in ("common", "rare", "epic"):
        tier = "common"
    mood = int(rec.get("mood", 50))
    hidden = bool(rec.get("hidden_bonus_applied"))
    flavor = rec.get("reward_flavor") or "一份谢礼。"
    rt = rec.get("reward_type", "gold")

    if rt == "gold":
        nominal = int(rec.get("reward_value", 8))
        base = min(nominal, {"common": 18, "rare": 30, "epic": 45}[tier])
        amount = clamp_gold_for_tier(base, tier, mood, hidden)
        player_gold_delta(amount)
        lines.append(f"获得金币 {amount}（{flavor}）")
    elif rt == "clue":
        clue = f"{rec['name']} 的线索：{rec['request'][:120]}…"
        memory_add(clue)
        lines.append(f"线索已记下：{flavor}")
        if hidden:
            lines.append("隐藏因缘：对方多透露了半句关键口风。")
    elif rt == "item":
        if tier == "common":
            item_id = "healing_potion"
        elif tier == "rare":
            item_id = "leather_armor"
        else:
            item_id = "healing_potion"
        try:
            it = catalog_item(item_id)
            player_add_item(it)
            lines.append(f"获得物品：{getattr(it, 'name', item_id)}（{flavor}）")
        except Exception:
            player_gold_delta(15)
            lines.append("谢礼难以交割，对方折成金币交给你。")
    elif rt == "stat":
        which = "charisma" if (mood >= 55) else "strength"
        delta = 1 if tier == "common" else 2 if tier == "rare" else 1
        delta = min(delta, 2)
        player_add_stat(which, delta)
        lines.append(f"属性提升：{which} +{delta}（{flavor}）")
    elif rt == "hidden_plot":
        lines.append(f"【异闻】{flavor}")
        if tier == "epic":
            lines.append("广场上的风忽然静下来一瞬——仿佛有双眼睛在雾后注视。")
        memory_add(f"广场异闻：{rec['name']} — {rec['request'][:100]}")
    else:
        player_gold_delta(10)
        lines.append("对方塞给你一把零钱。")

    return lines
