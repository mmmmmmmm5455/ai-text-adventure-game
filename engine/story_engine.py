"""
AI 故事引擎：LangGraph 组织单次场景描写生成；选择生成与结果处理。
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from loguru import logger

from core.i18n import t
from core.narrative_language import (
    get_narrative_language,
    scene_prompt_tail,
    scene_system_brief,
)
from engine.enhancement_engine import EnhancementEngine, maybe_record_world_flags_from_action
from engine.companion_gen import generate_companion_blueprint
from engine.companion_narrative import (
    generate_camp_whisper,
    generate_companion_fate_narrative,
    generate_probe_banter,
)
from engine.dynamic_npc_gen import generate_dynamic_npc_json
from engine.llm_client import LLMClient
from engine.memory_manager import MemoryManager
from game.dynamic_npc import (
    MAX_DYNAMIC_NPCS,
    apply_link_to_existing,
    blueprint_to_record,
    check_hidden_bonus,
    complete_dynamic_npc_quest,
    deliver_dynamic_quest_rewards,
    fallback_blueprint,
    parse_blueprint,
    remove_dynamic_npc_quest,
    roll_reward_tier,
    sync_dynamic_quest_progress,
)
from game.enhancements import bump_counter
from game.companion import (
    JOIN_GOLD_COST,
    apply_loyalty_delta,
    companion_record_from_blueprint,
    get_active_companion,
    resolve_companion_fate,
)
from game.game_state import GameState
from game.inventory import InventoryItem, ItemCategory
from game.player import item_healing_potion
from story import characters as ch
from story import scenes as sc
from story.endings import EndingInfo, decide_ending
from story.items import catalog
from story.world_config import get_world_lore


class _GraphState(TypedDict, total=False):
    """LangGraph 状态：场景描写生成。"""

    scene_id: str
    player_name: str
    profession: str
    time_label: str
    memories: str
    output: str


def _build_scene_graph(llm: LLMClient) -> Any:
    """构建用于生成场景描写的 LangGraph（单节点）。"""

    def node_generate(state: _GraphState) -> _GraphState:
        sid = state.get("scene_id", "village_square")
        scene = sc.get_scene(sid)
        name = sc.scene_name(sid)
        base = sc.scene_description(sid) if scene else ""
        mem = state.get("memories", "")
        system = scene_system_brief()
        prompt = (
            f"世界观：{get_world_lore()}\n"
            f"当前时间：{state.get('time_label', '')}\n"
            f"角色：{state.get('player_name', '旅人')}（{state.get('profession', '')}）\n"
            f"场景：{name}\n场景基调：{base}\n"
            f"相关记忆摘录：{mem or '无'}\n"
            f"{scene_prompt_tail()}"
        )
        out = llm.generate_text(prompt, system=system, temperature=0.75)
        return {**state, "output": out}

    graph = StateGraph(_GraphState)
    graph.add_node("generate", node_generate)
    graph.set_entry_point("generate")
    graph.add_edge("generate", END)
    return graph.compile()


@dataclass
class ChoiceOption:
    """玩家可选项。"""

    choice_id: str
    label: str


class StoryEngine:
    """对外故事引擎 API。"""

    def __init__(self) -> None:
        self.llm = LLMClient()
        self.memory = MemoryManager()
        self._graph = _build_scene_graph(self.llm)
        # 与 AIDialogueEngine 共用逻辑；供旧版 frontend 仅持有 StoryEngine 时仍可对话
        self._dialogue_eng: Any = None
        self._flavor_eng: EnhancementEngine | None = None

    @property
    def flavor(self) -> EnhancementEngine:
        if self._flavor_eng is None:
            self._flavor_eng = EnhancementEngine()
        return self._flavor_eng

    def _get_dialogue(self) -> Any:
        from engine.ai_dialogue import AIDialogueEngine

        if self._dialogue_eng is None:
            self._dialogue_eng = AIDialogueEngine()
        return self._dialogue_eng

    def _maybe_achievements(self, state: GameState) -> None:
        for t in self.flavor.drain_narrative_achievements(state):
            state.add_log(t[:220])

    def start_dialogue(self, state: GameState, npc_id: str) -> str:
        return self._get_dialogue().start_dialogue(state, npc_id)

    def continue_dialogue(self, state: GameState, session: Any, user_text: str) -> tuple[str, list[str]]:
        return self._get_dialogue().continue_dialogue(state, session, user_text)

    def end_dialogue(self, state: GameState, session: Any) -> str:
        return self._get_dialogue().end_dialogue(state, session)

    def try_intimidate(self, state: GameState, session: Any) -> tuple[str, int]:
        return self._get_dialogue().try_intimidate(state, session)

    def generate_scene_description(self, state: GameState) -> str:
        """生成当前场景描写（LangGraph 调用 LLM）。"""
        if not state.player:
            return (
                "(No character yet.)"
                if get_narrative_language() == "en"
                else "（尚未创建角色。）"
            )
        scene_id = state.current_scene_id
        mem_text = "；".join(self.memory.query_relevant(scene_id + " " + state.time_label(), k=3))
        try:
            out = self._graph.invoke(
                {
                    "scene_id": scene_id,
                    "player_name": state.player.name,
                    "profession": state.player.profession.value,
                    "time_label": state.time_label(),
                    "memories": mem_text,
                }
            )
            text = str(out.get("output", "")).strip()
            if text:
                self.memory.add_memory(
                    f"{state.player.name} 在 {scene_id}: {text[:200]}",
                    {"scene": scene_id},
                )
                return text
        except Exception as e:
            logger.exception("场景生成失败：{}", e)
        return self._static_scene_fallback(scene_id)

    def _static_scene_fallback(self, scene_id: str) -> str:
        s = sc.get_scene(scene_id)
        if not s:
            return (
                "You stand in a strange place; wind brushes past your ears."
                if get_narrative_language() == "en"
                else "你站在一片陌生之地，风声掠过耳畔。"
            )
        if get_narrative_language() == "en":
            return (
                f"You arrive at {sc.scene_name(scene_id)}. {sc.scene_description(scene_id)} "
                "Unease and anticipation mingle in the air—your next step will shape the tale."
            )
        return (
            f"你来到{sc.scene_name(scene_id)}。{sc.scene_description(scene_id)} "
            "空气里混杂着不安与期待，你的下一步将决定故事的走向。"
        )

    def generate_choices(self, state: GameState) -> list[ChoiceOption]:
        """为当前场景生成 4-6 个可执行选项。"""
        if not state.player:
            return []
        scene_id = state.current_scene_id
        scene = sc.get_scene(scene_id)
        choices: list[ChoiceOption] = []

        if scene:
            for ex in scene.exits:
                if ex in state.unlocked_scenes:
                    target = sc.get_scene(ex)
                    label = t("story.choice.go_to_named", name=sc.scene_name(ex)) if target else t(
                        "story.choice.go_to_id",
                        scene_id=ex,
                    )
                    choices.append(ChoiceOption(f"move:{ex}", label))

        for npc_id in ch.npc_for_scene(scene_id):
            prof = ch.NPCS.get(npc_id)
            name = prof.name if prof else npc_id
            choices.append(
                ChoiceOption(
                    f"talk:{npc_id}",
                    t("story.choice.talk", name=name),
                )
            )

        if scene_id == "village_square":
            choices.append(
                ChoiceOption(
                    "dyn_spawn",
                    t("story.choice.dyn_spawn"),
                )
            )
            for dn in state.dynamic_npcs:
                if dn.get("status") == "active" and int(dn.get("progress", 0)) >= int(
                    dn.get("objective_count", 1)
                ):
                    choices.append(
                        ChoiceOption(
                            f"dyn_deliver:{dn['id']}",
                            t("story.choice.dyn_deliver", name=dn.get("name", "passerby")),
                        )
                    )
                elif dn.get("status") == "fresh":
                    choices.append(
                        ChoiceOption(
                            f"dyn_resume:{dn['id']}",
                            t("story.choice.dyn_resume", name=dn.get("name", "passerby")),
                        )
                    )

        choices.append(ChoiceOption("search", t("story.choice.search")))
        choices.append(ChoiceOption("rest", t("story.choice.rest")))

        if state.player.inventory.has_item("healing_potion"):
            choices.append(ChoiceOption("use_potion", t("story.choice.use_potion")))

        if scene_id == "tavern":
            if not state.pending_companion_offer and get_active_companion(state) is None:
                choices.append(
                    ChoiceOption(
                        "companion_seek",
                        t("story.choice.seek_companion"),
                    )
                )
            choices.append(
                ChoiceOption(
                    "tavern_bribe",
                    t("story.choice.tavern_bribe"),
                ),
            )

        ac = get_active_companion(state)
        if ac:
            choices.append(
                ChoiceOption(
                    "companion_gift",
                    t("story.choice.gift_companion"),
                )
            )
            choices.append(
                ChoiceOption(
                    "companion_probe",
                    t("story.choice.probe_companion"),
                )
            )
            choices.append(
                ChoiceOption(
                    "companion_contract",
                    t("story.choice.contract_companion"),
                )
            )

        choices.append(ChoiceOption("ending", t("story.choice.ending")))

        return choices[:20]

    def process_choice(self, state: GameState, choice_id: str) -> tuple[str, bool]:
        """
        处理玩家选择，返回 (叙事文本, 是否进入对话模式)。
        进入对话模式时前端应切换到聊天 UI，并在 session 中记录 dialogue_npc。
        """
        if not state.player:
            return t("story.err.no_player"), False

        state.advance_round()

        if choice_id.startswith("move:"):
            target = choice_id.split(":", 1)[1]
            if target not in state.unlocked_scenes:
                return t("story.err.locked_scene"), False
            state.current_scene_id = target
            state.add_key_choice(f"移动至 {target}")
            state.add_log(t("story.log.reach_scene", target=target))
            bump_counter(state, "moves", 1)
            maybe_record_world_flags_from_action(state, "enter_scene", target)
            self._update_main_quest_on_move(state, target)
            self._maybe_achievements(state)
            return t("story.ret.move", target=target), False

        if choice_id.startswith("talk:"):
            npc_id = choice_id.split(":", 1)[1]
            state.add_log(t("story.log.start_talk", npc_id=npc_id))
            bump_counter(state, "npc_talks", 1)
            self._maybe_achievements(state)
            return t("story.ret.approach"), True

        if choice_id == "dyn_spawn":
            state.add_log(t("story.log.scan_crowd"))
            return self.spawn_dynamic_npc_encounter(state)

        if choice_id.startswith("dyn_resume:"):
            rid = choice_id.split(":", 1)[1]
            if any(n.get("id") == rid for n in state.dynamic_npcs):
                state.active_dynamic_npc_id = rid
                return t("story.ret.resume_talker"), False
            return t("story.ret.missing_talker"), False

        if choice_id.startswith("dyn_deliver:"):
            dnid = choice_id.split(":", 1)[1]
            return self._deliver_dynamic_npc(state, dnid)

        if choice_id == "search":
            return self._action_search(state)

        if choice_id == "rest":
            bump_counter(state, "rests", 1)
            state.player.heal(8)
            state.player.restore_mp(6)
            state.add_log(t("story.log.rested"))
            comp = get_active_companion(state)
            if comp:
                if "bribed_authority" in state.tags:
                    if comp.get("hidden_trait", {}).get("type") == "spy":
                        apply_loyalty_delta(comp, -4)
                        state.add_log(t("story.log.spy_bribe_reaction"))
                    state.tags.discard("bribed_authority")
                if random.random() < 0.16:
                    whisper = generate_camp_whisper(self.llm, comp)
                    state.add_log(t("story.log.camp_whisper", text=whisper[:220]))
                    apply_loyalty_delta(comp, random.choice([-2, 0, 1, 2, 4]))
            if random.random() < 0.28:
                dream = self.flavor.generate_dream(state)
                state.add_log(t("story.log.dream", text=f"{dream[:140]}..."))
            self._maybe_achievements(state)
            return t("story.ret.rest"), False

        if choice_id == "use_potion":
            err = state.player.use_consumable("healing_potion")
            if err:
                return err, False
            state.add_log(t("story.log.drink_potion"))
            return t("story.ret.drink_potion"), False

        if choice_id == "ending":
            info = decide_ending(state)
            return self._format_ending(info), False

        if choice_id == "companion_seek":
            if state.current_scene_id != "tavern":
                return t("story.err.no_tavern_crowd"), False
            if state.pending_companion_offer:
                return t("story.err.pending_companion"), False
            if get_active_companion(state):
                return t("story.err.already_has_companion"), False
            bp = generate_companion_blueprint(self.llm, state)
            state.pending_companion_offer = companion_record_from_blueprint(bp)
            state.add_log(t("story.log.hear_companion_name"))
            state.touch()
            return t("story.ret.companion_waiting"), False

        if choice_id == "tavern_bribe":
            if state.current_scene_id != "tavern":
                return t("story.err.no_bribe_here"), False
            if state.player.gold < 5:
                return t("story.err.not_enough_coins"), False
            state.player.gold -= 5
            state.add_tag("bribed_authority")
            state.add_key_choice("贿赂打听捷径")
            state.add_log(t("story.log.bribe_idlers"))
            return t("story.ret.bribe_hint"), False

        if choice_id == "companion_gift":
            comp = get_active_companion(state)
            if not comp:
                return t("story.err.no_companion_owned"), False
            if state.player.gold < 10:
                return t("story.err.not_enough_gift_gold"), False
            state.player.gold -= 10
            apply_loyalty_delta(comp, 8)
            state.add_log(t("story.log.companion_gift", name=comp.get("name", t("status.companion"))))
            return t("story.ret.companion_soften"), False

        if choice_id == "companion_probe":
            comp = get_active_companion(state)
            if not comp:
                return t("story.err.no_companion_active"), False
            line = generate_probe_banter(self.llm, comp)
            d = random.randint(-3, 5)
            apply_loyalty_delta(comp, d)
            if random.random() < 0.28:
                state.add_tag("companion_revealed")
                state.add_log(t("story.log.probe_reveal"))
            state.add_log(t("story.log.probe_line", text=line[:120]))
            return line, False

        if choice_id == "companion_contract":
            comp = get_active_companion(state)
            if not comp:
                return t("story.err.no_companion_active"), False
            if state.player.gold < 25:
                return t("story.err.contract_expensive"), False
            state.player.gold -= 25
            state.add_tag("companion_contract")
            apply_loyalty_delta(comp, 6)
            state.add_log(t("story.log.contract_signed"))
            return t("story.ret.contract_glow"), False

        return t("story.ret.nothing"), False

    def _action_search(self, state: GameState) -> tuple[str, bool]:
        """搜寻：可能推进支线或获得物品。"""
        bump_counter(state, "searches", 1)
        self._maybe_achievements(state)
        sid = state.current_scene_id
        if sid == "village_square":
            for npc in state.dynamic_npcs:
                if npc.get("status") == "active" and int(npc.get("progress", 0)) < int(
                    npc.get("objective_count", 1)
                ):
                    npc["progress"] = int(npc.get("progress", 0)) + 1
                    sync_dynamic_quest_progress(state, npc)
                    state.add_log(
                        t(
                            "story.log.square_progress",
                            name=npc.get("name", t("dyn.title")),
                            progress=npc["progress"],
                            total=npc.get("objective_count", 1),
                        )
                    )
                    state.touch()
                    break

        if sid == "misty_forest" and state.quests.get("side_merchant"):
            q = state.quests.get("side_merchant")
            if q and not q.completed and q.progress == 0:
                q.advance(1)
                state.player.gold += 5
                state.add_log(t("story.log.find_merchant_crate"))
                return t("story.ret.find_merchant_crate"), False

        if sid == "mountain_foot" and state.quests.get("side_miner_tool"):
            q = state.quests.get("side_miner_tool")
            if q and not q.completed and q.progress == 0:
                q.advance(1)
                state.add_log(t("story.log.find_miner_bag"))
                return t("story.ret.find_miner_bag"), False

        if sid == "tavern" and state.quests.get("side_elder_cat"):
            q = state.quests.get("side_elder_cat")
            if q and not q.completed and q.progress == 0:
                q.advance(1)
                state.add_log(t("story.log.find_cat"))
                return t("story.ret.find_cat"), False

        if sid == "mysterious_cave" and state.quests.get("main_forest"):
            q = state.quests.get("main_forest")
            if q and q.progress >= 2 and not state.player.inventory.has_item("ancient_key"):
                key = catalog()["ancient_key"]
                state.player.inventory.add_item(InventoryItem(**{**key.to_dict(), "quantity": 1}))
                state.add_log(t("story.log.find_key"))
                return t("story.ret.find_key"), False

        if sid == "underground_ruins" and state.player.inventory.has_item("ancient_key"):
            q = state.quests.get("main_forest")
            if q and not q.completed:
                q.progress = len(q.objectives)
                q.completed = True
                state.completed_quest_ids.add("main_forest")
                state.active_quest_ids.discard("main_forest")
                state.add_tag("main_complete")
                state.add_tag("hero_path")
                state.player.gain_xp(120)
                state.player.gold += 80
                if not state.player.inventory.has_item("treasure"):
                    tr = catalog()["treasure"]
                    state.player.inventory.add_item(InventoryItem(**{**tr.to_dict(), "quantity": 1}))
                state.add_log(t("story.log.main_complete"))
                state.pending_gift_box = True
                maybe_record_world_flags_from_action(state, "main_complete", "")
                return t("story.ret.main_complete"), False

        # 默认：随机一点金币或药水
        state.player.gold += 3
        state.add_log(t("story.log.search_scraps"))
        return t("story.ret.search_scraps"), False

    def generate_ending_narrative(self, state: GameState) -> str:
        """调用 LLM 扩写结局（在规则判定之后）。"""
        info = decide_ending(state)
        base = self._format_ending(info)
        if not state.player:
            return base
        if get_narrative_language() == "en":
            system = "You are a fantasy novelist. Write a warm or heavy closing passage in English."
            prompt = (
                f"Ending type: {info.title}\n"
                f"Summary: {info.summary}\n"
                f"Character: {state.player.name}, profession {state.player.profession.value}, level {state.player.level}\n"
                "Expand to 200–280 words in English; stay consistent with the summary; no modern technology."
            )
        else:
            system = "你是奇幻小说作者，用中文写温暖或沉重的收束段落。"
            prompt = (
                f"已知结局类型：{info.title}\n"
                f"摘要：{info.summary}\n"
                f"角色：{state.player.name}，职业 {state.player.profession.value}，等级 {state.player.level}\n"
                "请扩写为 200-280 字，保持与摘要一致，不要引入现代科技。"
            )
        try:
            text = self.llm.generate_text(prompt, system=system, temperature=0.8, max_tokens=700)
            if text:
                base = text.strip()
        except Exception as e:
            logger.warning("结局扩写失败：{}", e)

        comp = get_active_companion(state)
        if comp:
            rng = random.Random(state.round_count + len(comp.get("companion_id", "")))
            fate = resolve_companion_fate(state, comp, info, rng)
            fate_text = generate_companion_fate_narrative(self.llm, comp, info, fate)
            entry = {
                "companion_id": comp.get("companion_id"),
                "name": comp.get("name"),
                "betrayed": fate.betrayed,
                "twist": fate.twist_loyal_subversion,
                "reason": fate.reason_code,
                "summary": fate_text[:500],
            }
            state.companion_fate_log.append(entry)
            state.companion_fate_log = state.companion_fate_log[-5:]
            state.touch()
            base = f"{base}\n\n{t('story.label.companion_epilogue')}\n{fate_text}"
        return base

    def _format_ending(self, info: EndingInfo) -> str:
        if get_narrative_language() == "en":
            return f"[{info.title}]\n{info.summary}"
        return f"【{info.title}】\n{info.summary}"

    def _update_main_quest_on_move(self, state: GameState, new_scene: str) -> None:
        """主线：按抵达场景推进进度。"""
        q = state.quests.get("main_forest")
        if not q or q.completed:
            return
        milestones = {
            "misty_forest": 1,
            "mysterious_cave": 2,
            "underground_ruins": 3,
        }
        if new_scene not in milestones:
            return
        target = milestones[new_scene]
        if q.progress < target:
            q.progress = target

    def spawn_dynamic_npc_encounter(self, state: GameState) -> tuple[str, bool]:
        """生成一名动态路人并打开遭遇 UI（由前端根据 active_dynamic_npc_id 渲染）。"""
        if not state.player:
            return t("story.err.no_player"), False
        if state.current_scene_id != "village_square":
            return t("story.err.no_people_here"), False
        tier = roll_reward_tier()
        raw = generate_dynamic_npc_json(self.llm, state, tier)
        bp = parse_blueprint(raw) or fallback_blueprint(tier)
        rec = blueprint_to_record(bp, tier)
        apply_link_to_existing(rec, state.dynamic_npcs)
        if len(state.dynamic_npcs) >= MAX_DYNAMIC_NPCS:
            gone = state.dynamic_npcs.pop(0)
            remove_dynamic_npc_quest(state, str(gone.get("id", "")))
            state.add_log(t("story.log.passerby_leave", name=gone.get("name", t("dyn.title"))))
        state.dynamic_npcs.append(rec)
        state.active_dynamic_npc_id = rec["id"]
        state.add_log(t("story.log.notice_passerby", name=rec["name"]))
        state.touch()
        tip = ""
        if rec.get("linked_blurb"):
            tip = f"\n\n{rec['linked_blurb']}"
        return f"{rec['appearance']}\n\n「{rec['opening']}」{tip}", False

    def _deliver_dynamic_npc(self, state: GameState, dnid: str) -> tuple[str, bool]:
        rec = next((n for n in state.dynamic_npcs if n.get("id") == dnid), None)
        if not rec or rec.get("status") != "active":
            return t("story.err.no_deliver_request"), False
        need = int(rec.get("objective_count", 1))
        if int(rec.get("progress", 0)) < need:
            return t("story.err.deliver_progress_low", progress=rec.get("progress", 0), need=need), False
        if not state.player:
            return t("dialogue.err.ellipsis"), False

        cat = catalog()

        def add_gold(n: int) -> None:
            state.player.gold += n

        def add_item(it: InventoryItem) -> None:
            d = it.to_dict()
            state.player.inventory.add_item(InventoryItem(**{**d, "quantity": 1}))

        def add_stat(which: str, delta: int) -> None:
            if which == "charisma":
                state.player.charisma += delta
            else:
                state.player.strength += delta

        def mem_add(text: str) -> None:
            self.memory.add_memory(text, {"dynamic_npc": rec.get("id", "")})

        def cat_item(item_id: str) -> InventoryItem:
            return InventoryItem(**{**cat[item_id].to_dict(), "quantity": 1})

        lines = deliver_dynamic_quest_rewards(
            rec,
            player_gold_delta=add_gold,
            player_add_item=add_item,
            player_add_stat=add_stat,
            memory_add=mem_add,
            catalog_item=cat_item,
        )
        for line in lines:
            state.add_log(line)
        complete_dynamic_npc_quest(state, dnid)
        state.dynamic_npcs = [n for n in state.dynamic_npcs if n.get("id") != dnid]
        maybe_record_world_flags_from_action(state, "dynamic_deliver", "")
        state.touch()
        return t("story.ret.dynamic_delivered", name=rec.get("name", t("dyn.title"))), False


def grant_starting_items(state: GameState) -> None:
    """新游戏赠送基础物品。"""
    if not state.player:
        return
    pot = item_healing_potion()
    state.player.inventory.add_item(pot)
    state.player.inventory.add_item(
        InventoryItem(
            item_id="rusty_sword",
            name="生锈短剑",
            category=ItemCategory.WEAPON,
            quantity=1,
            description="新手武器。",
        )
    )
    state.player.equipped_weapon_id = "rusty_sword"


def accept_companion_offer(engine: StoryEngine, state: GameState) -> str:
    """接受待招募队友（不经过 process_choice 的回合推进）。"""
    if not state.pending_companion_offer or not state.player:
        return t("story.err.no_companion_offer")
    if state.player.gold < JOIN_GOLD_COST:
        return t("story.err.need_join_gold", gold=JOIN_GOLD_COST)
    state.player.gold -= JOIN_GOLD_COST
    rec = state.pending_companion_offer
    rec["party_status"] = "active"
    for c in state.companions:
        c["party_status"] = "inactive"
    state.companions.append(rec)
    state.pending_companion_offer = None
    state.add_log(t("story.log.companion_join", name=rec["name"]))
    engine.memory.add_memory(
        f"队友 {rec['name']}：{str(rec.get('personality', ''))[:100]}（真面目未明）",
        {"companion": rec["companion_id"]},
    )
    state.touch()
    return t("story.ret.companion_join", name=rec["name"])


def decline_companion_offer(state: GameState) -> str:
    if not state.pending_companion_offer:
        return t("dialogue.err.ellipsis")
    name = state.pending_companion_offer.get("name", "对方")
    state.pending_companion_offer = None
    state.touch()
    state.add_log(t("story.log.companion_decline", name=name))
    return t("story.ret.companion_decline", name=name)
