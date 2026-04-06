"""
统一 AI 风味事件：预言、报纸、梦境、骰子、占星、旋律、记忆回溯、第四面墙、地图演变叙事、礼物盒、成就叙事。
"""

from __future__ import annotations

import random
from typing import Any

from loguru import logger

from core.narrative_language import get_narrative_language, user_locale_tail
from engine.llm_client import LLMClient
from engine.memory_manager import shared_memory_manager
from game.enhancements import (
    NARRATIVE_ACHIEVEMENTS,
    append_world_evolution,
    bump_counter,
    record_flavor_event,
    set_world_flag,
)
from game.game_state import GameState
from game.inventory import InventoryItem, ItemCategory
from story.items import catalog
from story.world_config import get_world_lore


class EnhancementEngine:
    def __init__(self) -> None:
        self.llm = LLMClient()
        self.memory = shared_memory_manager()

    def _remember(self, text: str, meta: dict[str, Any]) -> None:
        t = text.strip()
        if len(t) > 12:
            self.memory.add_memory(t[:400], meta)

    def _ctx(self, state: GameState) -> str:
        p = state.player
        if not p:
            return ""
        return (
            f"玩家：{p.name}，{p.profession.value}，Lv{p.level}，"
            f"场景：{state.current_scene_id}，时段：{state.time_label()}。"
        )

    def generate_prophecy(self, state: GameState) -> str:
        """2～3 条模糊未来碎片，允许一条带误导感。"""
        recent = (state.key_choices[-2:] if state.key_choices else [])
        recent_s = "；".join(recent) or "（尚无重大抉择记录）"
        system = (
            "你是中世纪奇幻世界里的「残卷预言者」。只输出叙事正文，不要 JSON。\n"
            "写 2～3 段，每段以「◆ 若……」开头，描写可能的未来碎片，语气模糊如诗。\n"
            "至少一段可以是后来被证明为误导的幻象或断章取义；禁止现代科技与网络梗。"
        )
        user = (
            f"{get_world_lore()}\n{self._ctx(state)}\n最近抉择摘要：{recent_s}\n请写预言碎片。"
            + user_locale_tail()
        )
        try:
            t = self.llm.generate_text(user, system=system, temperature=0.88, max_tokens=520)
            if t.strip():
                record_flavor_event(state, "prophecy", t.strip())
                self._remember(f"预言残卷：{t[:200]}", {"flavor": "prophecy"})
                return t.strip()
        except Exception as e:
            logger.warning("预言生成失败，使用降级文案：{}", e)
        if get_narrative_language() == "en":
            fb = (
                "◆ If you lend a hand, a distant letter rustles on the wind as if in thanks.\n"
                "◆ If you walk away, years later eyes may meet yours in the rain, half remembered.\n"
                "◆ If neither—the page burns here, and the future stays blank."
            )
        else:
            fb = (
                "◆ 若你伸手相助，风中会传来远方的信笺声，像有人在谢你。\n"
                "◆ 若你转身离去，许多年后雨里会有一双眼睛与你对视，似曾相识。\n"
                "◆ 若你两者皆非——残页在此燃尽，未来仍空白。"
            )
        record_flavor_event(state, "prophecy", fb)
        return fb

    def generate_newspaper(self, state: GameState, issue: int) -> str:
        system = (
            "你是奇幻小镇「时空小报」的撰稿人。只输出叙事正文，不要 JSON。\n"
            "写一则小报：标题行、3～4 条短讯（广告/八卦/警告/匿名信），"
            "其中可混入一条明显荒诞或假的启事增加趣味；禁止现代科技品牌。"
        )
        user = f"{get_world_lore()}\n{self._ctx(state)}\n期号：第 {issue} 期。" + user_locale_tail()
        try:
            t = self.llm.generate_text(user, system=system, temperature=0.9, max_tokens=480)
            if t.strip():
                record_flavor_event(state, "newspaper", t.strip())
                self._remember(f"时空小报{issue}：{t[:160]}", {"flavor": "newspaper"})
                return t.strip()
        except Exception as e:
            logger.warning("时空小报生成失败，使用降级文案：{}", e)
        fb = (
            f"【时空小报】第{issue}期\n"
            "⚡ 旧井边有人收购「会唱歌的石头」——真假自辨。\n"
            "⚡ 森林边缘夜行客增多，守卫换班加密。\n"
            "⚡ 匿名：别信上一则广告，那是三年前的人写的。\n"
        )
        record_flavor_event(state, "newspaper", fb)
        return fb

    def generate_dream(self, state: GameState) -> str:
        kinds = ("预知", "警告", "回忆", "无意义的瑰丽混沌")
        k = random.choice(kinds)
        system = (
            "你是奇幻梦境书写者。只输出一段 3～6 句梦境，不要标题外的解释。\n"
            "禁止现代科技；梦境可晦涩，未必与真实剧情一致。"
        )
        user = f"{get_world_lore()}\n{self._ctx(state)}\n梦境倾向：{k}。" + user_locale_tail()
        try:
            t = self.llm.generate_text(user, system=system, temperature=0.92, max_tokens=360)
            if t.strip():
                record_flavor_event(state, "dream", t.strip())
                self._remember(f"梦境：{t[:180]}", {"flavor": "dream"})
                return t.strip()
        except Exception as e:
            logger.warning("梦境生成失败，使用降级文案：{}", e)
        fb = "你在无数镜面里看见自己，每一张脸都在说不同的话；碎裂声里你惊醒，心口仍有余悸。"
        record_flavor_event(state, "dream", fb)
        return fb

    def generate_fate_dice(self, state: GameState) -> tuple[int, str]:
        roll = random.randint(1, 6)
        system = (
            "你是「命运骰子」的解说者。玩家掷出 1～6 点之一。只输出 2～4 句诗性解读，"
            "点越大机遇与风险并存；不要编造具体数值奖励。禁止现代科技。"
        )
        user = f"{get_world_lore()}\n{self._ctx(state)}\n骰点：{roll}" + user_locale_tail()
        try:
            t = self.llm.generate_text(user, system=system, temperature=0.85, max_tokens=240)
            if t.strip():
                body = f"你掷出命运骰子……停在 **{roll}** 点。\n\n{t.strip()}"
                record_flavor_event(state, "fate_dice", body)
                return roll, body
        except Exception as e:
            logger.warning("命运骰子解读失败，使用降级文案：{}", e)
        body = f"你掷出命运骰子……停在 **{roll}** 点。\n\n「{roll}」在旧书里代表变数：门会开，但未必通向你想去的地方。"
        record_flavor_event(state, "fate_dice", body)
        return roll, body

    def generate_astrology(self, state: GameState, birth_sign: str) -> str:
        system = (
            "你是奇幻占星师。根据玩家给出的生辰/星座自述（可虚构），写一段简短占星判词："
            "特质、命运倾向、一句警示；强调「倾向非定数」。只输出叙事正文。禁止现代科技。"
        )
        user = (
            f"{get_world_lore()}\n{self._ctx(state)}\n玩家自述生辰/星象：{birth_sign[:200]}"
            + user_locale_tail()
        )
        try:
            t = self.llm.generate_text(user, system=system, temperature=0.82, max_tokens=320)
            if t.strip():
                record_flavor_event(state, "astrology", t.strip())
                return t.strip()
        except Exception as e:
            logger.warning("占星解读失败，使用降级文案：{}", e)
        fb = "主星黯淡却有余晖：你善于在迷雾里找路，却易在平静时生疑。命运将在「真相」与「安宁」之间要你表态——但星盘可改，心亦可改。"
        record_flavor_event(state, "astrology", fb)
        return fb

    def generate_melody_reading(self, state: GameState, hummed: str) -> str:
        system = (
            "你是解读「哼唱旋律」秘文的乐灵。玩家输入任意哼唱文本。写 2～4 句："
            "可能像线索，也可能只是情绪回声；不要断言必然发生。禁止现代科技。"
        )
        user = f"{get_world_lore()}\n{self._ctx(state)}\n哼唱：{hummed[:400]}" + user_locale_tail()
        try:
            t = self.llm.generate_text(user, system=system, temperature=0.88, max_tokens=280)
            if t.strip():
                record_flavor_event(state, "melody", t.strip())
                return t.strip()
        except Exception as e:
            logger.warning("旋律解读失败，使用降级文案：{}", e)
        fb = "那串音节像远处的门环响了一下，又像是童年某段记不清的歌。你抓不住意义，只留下一阵恍惚。"
        record_flavor_event(state, "melody", fb)
        return fb

    def generate_memory_echo(self, state: GameState) -> str:
        system = (
            "你书写一段「记忆回溯」：可能是前世/平行时空的闪回，也可能是错觉。"
            "4～7 句，画面感强，不要点破真假。禁止现代科技。"
        )
        user = f"{get_world_lore()}\n{self._ctx(state)}" + user_locale_tail()
        try:
            t = self.llm.generate_text(user, system=system, temperature=0.9, max_tokens=400)
            if t.strip():
                record_flavor_event(state, "memory_echo", t.strip())
                self._remember(f"记忆闪回：{t[:200]}", {"flavor": "memory_echo"})
                return t.strip()
        except Exception as e:
            logger.warning("记忆回溯生成失败，使用降级文案：{}", e)
        fb = "火光照亮断裂的剑刃，你看见一双眼与己相同——那不是今日的你，却让你胸口吃痛。醒来时，掌心空无一物。"
        record_flavor_event(state, "memory_echo", fb)
        return fb

    def generate_meta_whisper(self, state: GameState) -> str | None:
        if int(getattr(state, "meta_break_budget", 0)) <= 0:
            return None
        system = (
            "你打破第四面墙：以叙事者或角色的口吻，写 2～4 句，暗示「被注视」或「故事之外的存在」，"
            "略带诡异或幽默，不要辱骂玩家，不要提现实公司名。禁止现代科技产品名。"
        )
        user = f"{get_world_lore()}\n{self._ctx(state)}" + user_locale_tail()
        try:
            t = self.llm.generate_text(user, system=system, temperature=0.95, max_tokens=260)
            if t.strip():
                state.meta_break_budget = int(state.meta_break_budget) - 1
                body = f"【虚空低语】\n{t.strip()}"
                record_flavor_event(state, "meta", body)
                state.touch()
                return body
        except Exception as e:
            logger.warning("虚空低语生成失败，使用降级文案：{}", e)
        state.meta_break_budget = int(state.meta_break_budget) - 1
        body = "【虚空低语】\n有谁在翻页——不是你，也不是风。你忽然不确定，刚才的选择是否只属于你。"
        record_flavor_event(state, "meta", body)
        state.touch()
        return body

    def generate_world_map_narrative(self, state: GameState) -> str:
        wf = dict(getattr(state, "world_flags", {}) or {})
        system = (
            "你是世界志记录者。根据给定的世界状态标记，写一段「地图与氛围的演变」描写，"
            "4～8 句，体现玩家行为带来的可见变化；可含矛盾张力。禁止现代科技。"
        )
        user = f"{get_world_lore()}\n{self._ctx(state)}\n世界标记：{wf}" + user_locale_tail()
        try:
            t = self.llm.generate_text(user, system=system, temperature=0.8, max_tokens=420)
            if t.strip():
                record_flavor_event(state, "world_map", t.strip())
                append_world_evolution(state, t.strip()[:400])
                return t.strip()
        except Exception as e:
            logger.warning("世界演变叙事生成失败，使用降级文案：{}", e)
        fb = "村庄的灯火比往日更密，而森林一线的哨影也多了。有人说这是安宁的前奏，也有人说是风暴在排队。"
        record_flavor_event(state, "world_map", fb)
        append_world_evolution(state, fb[:400])
        return fb

    def open_fate_gift_box(self, state: GameState) -> str:
        """代码决定奖励，模型只包装描写。"""
        if not state.player or not getattr(state, "pending_gift_box", False):
            return (
                "No fate gift box awaits you."
                if get_narrative_language() == "en"
                else "没有待开启的命运礼物盒。"
            )
        state.pending_gift_box = False
        cat = catalog()
        r = random.random()
        outcome_kind = ""
        if r < 0.22:
            outcome_kind = "empty"
            reward_line = "盒底空无一物，只余一缕干花的香——像在说，期待本身已是礼物。"
        elif r < 0.45:
            outcome_kind = "potion"
            pot = cat["healing_potion"]
            state.player.inventory.add_item(InventoryItem(**{**pot.to_dict(), "quantity": 1}))
            reward_line = "你摸到一瓶冰凉的药水，封蜡上刻着看不清的祝福。"
        elif r < 0.68:
            outcome_kind = "gold"
            g = random.randint(28, 55)
            state.player.gold += g
            reward_line = f"沉甸甸的金币在布里作响——约 {g} 枚。"
        elif r < 0.82:
            outcome_kind = "curse_hook"
            state.add_tag("gift_box_whisper")
            state.player.gain_xp(25)
            reward_line = "一枚黑石贴在掌心，低语顺着血脉爬上来……你获得经验，却也感到某种注视。"
        else:
            outcome_kind = "key_or_gold"
            if not state.player.inventory.has_item("ancient_key"):
                key = cat["ancient_key"]
                state.player.inventory.add_item(InventoryItem(**{**key.to_dict(), "quantity": 1}))
                reward_line = "一把旧钥匙躺在丝绒上，齿痕与洞穴传说隐隐相合。"
            else:
                state.player.gold += 40
                reward_line = "你已持有关键之物，盒中折为金叶补偿。"

        system = (
            "Polish the unboxing moment in 1–2 sentences in English. Do not change factual rewards."
            if get_narrative_language() == "en"
            else "用 1～2 句中文润色开箱瞬间的氛围，不要改事实奖励描述。禁止现代科技。"
        )
        user = f"开箱类型：{outcome_kind}。事实：{reward_line}" + user_locale_tail()
        try:
            wrap = self.llm.generate_text(user, system=system, temperature=0.75, max_tokens=120)
            if wrap.strip():
                body = f"【命运礼物盒】\n{wrap.strip()}\n{reward_line}"
                record_flavor_event(state, "gift_box", body)
                state.add_log("你开启了命运礼物盒。")
                state.touch()
                return body
        except Exception as e:
            logger.warning("命运礼物盒润色失败，使用事实文案：{}", e)
        body = f"【命运礼物盒】\n{reward_line}"
        record_flavor_event(state, "gift_box", body)
        state.add_log("你开启了命运礼物盒。")
        state.touch()
        return body

    def _try_one_narrative_achievement(self, state: GameState) -> str | None:
        unlocked = set(getattr(state, "narrative_achievement_ids", []) or [])
        counters = dict(getattr(state, "stat_counters", {}) or [])
        for aid, ckey, need, title in NARRATIVE_ACHIEVEMENTS:
            if aid in unlocked:
                continue
            if int(counters.get(ckey, 0)) < need:
                continue
            if get_narrative_language() == "en":
                system = (
                    f"Write a short narrative achievement story (80–140 words) in English; title must include 「{title}」. "
                    "No bullet lists; no system voice; no modern technology."
                )
            else:
                system = (
                    f"用中文写一段「叙事化成就」小故事 80～140 字，标题含「{title}」。"
                    "不要列表，不要系统腔；禁止现代科技。"
                )
            user = (
                f"{get_world_lore()}\n{self._ctx(state)}\n成就：{title}（{ckey} 达 {need} 次）"
                + user_locale_tail()
            )
            try:
                story = self.llm.generate_text(user, system=system, temperature=0.82, max_tokens=320)
                if not story.strip():
                    raise ValueError("empty")
            except Exception:
                if get_narrative_language() == "en":
                    story = (
                        f"【{title}】\nHabit made from many ordinary choices—"
                        "until one day you notice habit itself bending fate."
                    )
                else:
                    story = (
                        f"【{title}】\n你把许多个平凡的选择走成了习惯——"
                        "直到有一天你发现，习惯本身已在悄悄改写你的命运。"
                    )
            unlocked.add(aid)
            state.narrative_achievement_ids = sorted(unlocked)
            record_flavor_event(state, f"achievement_{aid}", story.strip())
            state.add_log(f"叙事成就：{title}")
            state.touch()
            return story.strip()
        return None

    def drain_narrative_achievements(self, state: GameState) -> list[str]:
        out: list[str] = []
        while True:
            one = self._try_one_narrative_achievement(state)
            if not one:
                break
            out.append(one)
        return out


def maybe_record_world_flags_from_action(state: GameState, action: str, detail: str = "") -> None:
    """在关键行动后更新世界标记（供地图演变叙事使用）。"""
    if action == "enter_scene" and detail == "misty_forest":
        if not (getattr(state, "world_flags", {}) or {}).get("visited_misty"):
            set_world_flag(state, "visited_misty", True)
            set_world_flag(state, "forest_whispers", "玩家首次踏入迷雾森林")
    if action == "main_complete":
        set_world_flag(state, "relics_sealed", True)
        set_world_flag(state, "village_mood", "异象消退后的松弛与敬畏")
    if action == "dynamic_deliver":
        n = int((getattr(state, "world_flags", {}) or {}).get("strangers_helped", 0))
        set_world_flag(state, "strangers_helped", n + 1)
