"""
长期记忆：Chroma 持久化 + Ollama 嵌入；失败时降级为内存列表。
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from loguru import logger

from core.config import get_settings
from engine.llm_client import ollama_embed_text


class MemoryManager:
    """管理玩家记忆片段的写入与相似度检索。"""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._collection = None
        self._client = None
        self._fallback: list[dict[str, Any]] = []
        self._init_chroma()

    def _init_chroma(self) -> None:
        try:
            import chromadb

            self._client = chromadb.PersistentClient(path=str(self._settings.chroma_dir))
            self._collection = self._client.get_or_create_collection(
                name="player_memories",
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("Chroma 记忆库已就绪：{}", self._settings.chroma_dir)
        except Exception as e:
            logger.warning("Chroma 初始化失败，使用内存降级：{}", e)
            self._collection = None
            self._client = None

    def add_memory(self, text: str, meta: dict[str, Any] | None = None) -> None:
        """写入一条记忆。"""
        text = text.strip()
        if not text:
            return
        meta = meta or {}
        emb = ollama_embed_text(text)
        if self._collection is not None and emb:
            mid = str(uuid4())
            self._collection.add(
                ids=[mid],
                documents=[text],
                embeddings=[emb],
                metadatas=[meta],
            )
            return
        self._fallback.append({"id": str(uuid4()), "text": text, "meta": meta})
        if len(self._fallback) > 500:
            self._fallback = self._fallback[-400:]

    def query_relevant(self, query: str, k: int = 4) -> list[str]:
        """检索与查询最相关的记忆文本。"""
        query = query.strip()
        if not query:
            return []
        emb = ollama_embed_text(query)
        if self._collection is not None and emb:
            try:
                res = self._collection.query(query_embeddings=[emb], n_results=k)
                docs = res.get("documents") or []
                if docs and docs[0]:
                    return [d for d in docs[0] if d]
            except Exception as e:
                logger.warning("Chroma 查询失败：{}", e)
        # 降级：简单关键词重叠
        words = set(query.replace("，", " ").split())
        scored: list[tuple[int, str]] = []
        for row in reversed(self._fallback):
            t = row["text"]
            score = sum(1 for w in words if w and w in t)
            scored.append((score, t))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:k] if t]
