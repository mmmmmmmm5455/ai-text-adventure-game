"""
AI 故事引擎：LangGraph 组织单次场景描写生成；选择生成与结果处理。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from loguru import logger

from engine.llm_client import LLMClient
from engine.memory_manager import MemoryManager
from game.game_state import GameState
from game.inventory import InventoryItem, ItemCategory
from game.player import item_healing_potion
from story import characters as ch
from story import scenes as sc
from story.endings import EndingInfo, decide_ending
from story.items import catalog
from story.world_config import WORLD_LORE


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
        scene = sc.get_scene(state.get("scene_id", "village_square"))
        name = scene.name if scene else "未知之地"
        base = scene.description if scene else ""
        mem = state.get("memories", "")
        system = (
            "你是中世纪奇幻世界的叙事者，文风克制、有画面感。"
            "禁止出现现代网络用语或与奇幻村庄无关的内容。"
        )
        prompt = (
            f"世界观：{WORLD_LORE}\n"
            f"当前时间：{state.get('time_label', '')}\n"
            f"角色：{state.get('player_name', '旅人')}（{state.get('profession', '')}）\n"
            f"场景：{name}\n场景基调：{base}\n"
            f"相关记忆摘录：{mem or '无'}\n"
            "请用中文写一段 120-180 字的沉浸式场景描写，不要给选项或总结。"
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

    def generate_scene_description(self, state: GameState) -> str:
        """生成当前场景描写（LangGraph 调用 LLM）。"""
        if not state.player:
            return "（尚未创建角色。）"
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
            return "你站在一片陌生之地，风声掠过耳畔。"
        return (
            f"你来到{s.name}。{s.description} "
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
                    label = f"前往「{target.name}」" if target else f"前往 {ex}"
                    choices.append(ChoiceOption(f"move:{ex}", label))

        for npc_id in ch.npc_for_scene(scene_id):
            prof = ch.NPCS.get(npc_id)
            name = prof.name if prof else npc_id
            choices.append(ChoiceOption(f"talk:{npc_id}", f"与{name}交谈"))

        choices.append(ChoiceOption("search", "搜寻周围线索"))
        choices.append(ChoiceOption("rest", "休息片刻（恢复少量生命与能量）"))

        if state.player.inventory.has_item("healing_potion"):
            choices.append(ChoiceOption("use_potion", "使用治疗药水"))

        choices.append(ChoiceOption("ending", "请求结局判定（完成故事）"))

        return choices[:10]

    def process_choice(self, state: GameState, choice_id: str) -> tuple[str, bool]:
        """
        处理玩家选择，返回 (叙事文本, 是否进入对话模式)。
        进入对话模式时前端应切换到聊天 UI，并在 session 中记录 dialogue_npc。
        """
        if not state.player:
            return "角色不存在。", False

        state.advance_round()

        if choice_id.startswith("move:"):
            target = choice_id.split(":", 1)[1]
            if target not in state.unlocked_scenes:
                return "你还不能前往该区域。", False
            state.current_scene_id = target
            state.add_key_choice(f"移动至 {target}")
            state.add_log(f"抵达场景：{target}")
            self._update_main_quest_on_move(state, target)
            return f"你动身前往新的地点……（{target}）", False

        if choice_id.startswith("talk:"):
            npc_id = choice_id.split(":", 1)[1]
            state.add_log(f"开始与 NPC 对话：{npc_id}")
            return "你靠近对方，准备开口……", True

        if choice_id == "search":
            return self._action_search(state)

        if choice_id == "rest":
            state.player.heal(8)
            state.player.restore_mp(6)
            state.add_log("你稍作休整，恢复了些许气力。")
            return "你坐下来调整呼吸，疲惫感稍稍退去。", False

        if choice_id == "use_potion":
            err = state.player.use_consumable("healing_potion")
            if err:
                return err, False
            state.add_log("你喝下治疗药水，伤口慢慢收敛。")
            return "药水滑过喉咙，温暖在体内扩散。", False

        if choice_id == "ending":
            info = decide_ending(state)
            return self._format_ending(info), False

        return "什么也没有发生。", False

    def _action_search(self, state: GameState) -> tuple[str, bool]:
        """搜寻：可能推进支线或获得物品。"""
        sid = state.current_scene_id
        if sid == "misty_forest" and state.quests.get("side_merchant"):
            q = state.quests.get("side_merchant")
            if q and not q.completed and q.progress == 0:
                q.advance(1)
                state.player.gold += 5
                state.add_log("你找到了商人遗失的一箱货物（进度已更新）。")
                return "树桩旁掩着一只摔裂的木箱，里面装着尚可辨认的织物与香料。", False

        if sid == "mountain_foot" and state.quests.get("side_miner_tool"):
            q = state.quests.get("side_miner_tool")
            if q and not q.completed and q.progress == 0:
                q.advance(1)
                state.add_log("你找到了矿工的工具袋。")
                return "路边草丛里挂着一个磨损的皮袋，叮当作响。", False

        if sid == "tavern" and state.quests.get("side_elder_cat"):
            q = state.quests.get("side_elder_cat")
            if q and not q.completed and q.progress == 0:
                q.advance(1)
                state.add_log("一只小猫从木桶后探出头来。")
                return "你在旅店后巷听见细弱的喵声，一只脏兮兮的猫蹭过你的靴边。", False

        if sid == "mysterious_cave" and state.quests.get("main_forest"):
            q = state.quests.get("main_forest")
            if q and q.progress >= 2 and not state.player.inventory.has_item("ancient_key"):
                key = catalog()["ancient_key"]
                state.player.inventory.add_item(InventoryItem(**{**key.to_dict(), "quantity": 1}))
                state.add_log("你拾起了古老钥匙。")
                return "你在潮湿石缝里摸到一把冰冷的钥匙，符文微微发光。", False

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
                state.add_log("主线完成：你封印了遗迹深处的躁动。")
                return "遗迹深处光芒骤亮，随后归于平静——村庄的异象随之消退。", False

        # 默认：随机一点金币或药水
        state.player.gold += 3
        state.add_log("你仔细搜索，只找到一些零钱与碎屑。")
        return "你翻找了一番，只发现几枚铜币与破碎的陶片。", False

    def generate_ending_narrative(self, state: GameState) -> str:
        """调用 LLM 扩写结局（在规则判定之后）。"""
        info = decide_ending(state)
        base = self._format_ending(info)
        if not state.player:
            return base
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
                return text.strip()
        except Exception as e:
            logger.warning("结局扩写失败：{}", e)
        return base

    def _format_ending(self, info: EndingInfo) -> str:
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
