"""
AI 对话引擎：LangChain ChatOllama 对话链；好感度与对话窗口；失败时降级。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from loguru import logger

from core.config import get_settings
from engine.llm_client import LLMClient
from engine.memory_manager import MemoryManager
from game.game_state import GameState
from story import characters as ch


@dataclass
class DialogueSession:
    """单次 NPC 对话会话。"""

    npc_id: str
    affinity: int = 0
    history: list[tuple[str, str]] = field(default_factory=list)  # (role, content) role: user/assistant

    def add_turn(self, role: str, content: str) -> None:
        self.history.append((role, content))
        # 最多保留 20 条消息（约 10 轮）
        if len(self.history) > 20:
            self.history = self.history[-20:]

    def export_text(self) -> str:
        lines = []
        for role, content in self.history:
            who = "玩家" if role == "user" else "NPC"
            lines.append(f"{who}：{content}")
        return "\n".join(lines)


class AIDialogueEngine:
    """NPC 对话：开场、继续、结束。"""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._fallback = LLMClient()
        self.memory = MemoryManager()

    def _chat_model(self) -> ChatOllama:
        return ChatOllama(
            base_url=self._settings.ollama_base_url,
            model=self._settings.ollama_model,
            timeout=self._settings.ollama_timeout,
        )

    def start_dialogue(self, state: GameState, npc_id: str) -> str:
        """生成开场白。"""
        prof = ch.NPCS.get(npc_id)
        if not prof:
            return "对方似乎不在此处。"
        mem = "；".join(self.memory.query_relevant(prof.name + " " + prof.background, k=3))
        system = (
            f"你是 NPC「{prof.name}」，身份：{prof.role}。"
            f"性格：{prof.personality}。背景：{prof.background}。"
            "只输出角色台词与动作描写，不要输出系统提示或括号解释模型自身。"
        )
        user = (
            f"世界观：森林边缘村庄与异象。\n相关记忆：{mem or '无'}\n"
            f"玩家：{state.player.name if state.player else '旅人'} 走近你。"
            "请用中文给出 2-4 句开场，体现你的说话风格。"
        )
        try:
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "{system}"),
                    ("human", "{user}"),
                ]
            )
            chain = prompt | self._chat_model() | StrOutputParser()
            text = chain.invoke({"system": system, "user": user}).strip()
            if text:
                return text
        except Exception as e:
            logger.warning("对话开场失败，使用降级：{}", e)
        return (
            f"{prof.name}抬起眼，打量着你："
            f"“{state.player.name if state.player else '旅人'}，你也听见森林里的声音了吗？”"
        )

    def continue_dialogue(
        self,
        state: GameState,
        session: DialogueSession,
        user_text: str,
    ) -> tuple[str, list[str]]:
        """
        继续对话：返回 (NPC 回复, 线索列表)。
        """
        prof = ch.NPCS.get(session.npc_id)
        if not prof:
            return "……（没有回应）", []

        session.add_turn("user", user_text)
        hist = session.export_text()
        system = (
            f"你是 NPC「{prof.name}」，{prof.role}。"
            f"性格：{prof.personality}。背景：{prof.background}。"
            "根据玩家话语自然回应，可埋下一条线索。不要跳出角色。"
        )
        user = f"对话记录：\n{hist}\n请用中文回复，长度适中。"
        reply = ""
        try:
            prompt = ChatPromptTemplate.from_messages(
                [("system", "{system}"), ("human", "{user}")],
            )
            chain = prompt | self._chat_model() | StrOutputParser()
            reply = chain.invoke({"system": system, "user": user}).strip()
        except Exception as e:
            logger.warning("对话继续失败：{}", e)
            reply = self._fallback.generate_text(
                f"玩家说：{user_text}\n请以{prof.name}口吻回应。",
                system=system,
            )

        session.add_turn("assistant", reply)
        session.affinity += self._affinity_delta(user_text, reply)
        clues = self._extract_clues(reply)
        if clues:
            self.memory.add_memory(
                f"{prof.name} 透露线索：{'；'.join(clues)}",
                {"npc": session.npc_id},
            )
        return reply, clues

    def end_dialogue(self, state: GameState, session: DialogueSession) -> str:
        """结束语。"""
        prof = ch.NPCS.get(session.npc_id)
        if not prof:
            return "你转身离开。"
        if session.affinity >= 3:
            state.player.gold += 5
            state.add_log(f"你与 {prof.name} 谈得投机，对方塞给你几枚铜币。")
        return f"{prof.name}点了点头：“路上小心。”"

    def _affinity_delta(self, user_text: str, reply: str) -> int:
        """简单好感度：正向词加分，负向词减分。"""
        pos = ("谢谢", "拜托", "愿意", "帮助", "理解")
        neg = ("滚", "蠢", "闭嘴", "讨厌")
        delta = 0
        for p in pos:
            if p in user_text:
                delta += 1
        for n in neg:
            if n in user_text:
                delta -= 2
        if len(reply) > 80:
            delta += 1
        return max(-2, min(3, delta))

    def _extract_clues(self, reply: str) -> list[str]:
        """从回复中提取简短线索句（启发式）。"""
        parts = re.split(r"[。！？\n]", reply)
        clues = [p.strip() for p in parts if len(p.strip()) >= 8 and any(
            k in p for k in ("森林", "洞穴", "钥匙", "遗迹", "雾", "符文", "矿", "旅店", "广场")
        )]
        return clues[:3]
