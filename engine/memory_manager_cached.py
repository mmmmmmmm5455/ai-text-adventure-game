"""
长期记忆：Chroma 持久化 + Ollama 嵌入；失败时降级为内存列表。
带缓存优化和批量查询支持。
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4
from datetime import timedelta

from loguru import logger

from core.config import get_settings
from engine.llm_client import ollama_embed_text
from engine.performance_cache import (
    cached,
    MEMORY_QUERY_CACHE,
    EMBEDDING_CACHE,
    make_memory_query_key,
    make_embedding_key,
)
from engine.batch_query import BatchMemoryQuery, BatchEmbedding


class CachedMemoryManager:
    """带缓存优化的记忆管理器"""

    def __init__(self, enable_cache: bool = True) -> None:
        self._settings = get_settings()
        self._collection = None
        self._client = None
        self._fallback: list[dict[str, Any]] = []
        self._enable_cache = enable_cache
        self._init_chroma()

        # 批量查询处理器
        self._batch_query = BatchMemoryQuery(self)
        self._batch_embedding = BatchEmbedding(ollama_embed_text)

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

        # 使用批量嵌入生成（带缓存）
        emb = self._get_embedding(text)

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

    def _get_embedding(self, text: str) -> list[float] | None:
        """获取文本嵌入（带缓存）"""
        if not self._enable_cache:
            return ollama_embed_text(text)

        # 检查缓存
        key = make_embedding_key(text)
        cached = EMBEDDING_CACHE.get(key)
        if cached is not None:
            return cached

        # 缓存未命中，生成嵌入
        emb = ollama_embed_text(text)
        if emb:
            EMBEDDING_CACHE.set(key, emb, ttl=timedelta(minutes=30))

        return emb

    def query_relevant(self, query: str, k: int = 4) -> list[str]:
        """检索与查询最相关的记忆文本（带缓存）。"""
        query = query.strip()
        if not query:
            return []

        if not self._enable_cache:
            return self._query_without_cache(query, k)

        # 检查缓存
        key = make_memory_query_key(query, k)
        cached = MEMORY_QUERY_CACHE.get(key)
        if cached is not None:
            return cached

        # 缓存未命中，执行查询
        results = self._query_without_cache(query, k)

        # 存入缓存
        if results:
            MEMORY_QUERY_CACHE.set(key, results, ttl=timedelta(minutes=5))

        return results

    def _query_without_cache(self, query: str, k: int) -> list[str]:
        """不使用缓存的查询（内部方法）"""
        emb = self._get_embedding(query)

        if self._collection is not None and emb:
            try:
                res = self._collection.query(query_embeddings=[emb], n_results=k)
                docs = res.get("documents") or []
                if docs and docs[0]:
                    return [d for d in docs[0] if d]
            except Exception as e:
                logger.warning("Chroma 查询失败：{}", e)

        # 降级到内存列表
        words = set(query.replace("，", " ").split())
        scored: list[tuple[int, str]] = []
        for row in reversed(self._fallback):
            t = row["text"]
            score = sum(1 for w in words if w and w in t)
            scored.append((score, t))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:k] if t]

    def query_batch(self, queries: list[str], k: int = 4) -> dict[str, list[str]]:
        """批量查询记忆

        Args:
            queries: 查询列表
            k: 每个查询返回结果数量

        Returns:
            查询结果字典 {query: [results]}
        """
        if not self._enable_cache:
            # 不使用缓存，逐个查询
            return {q: self._query_without_cache(q, k) for q in queries}

        # 使用批量查询处理器
        return self._batch_query.query_batch(queries, k, use_cache=True)

    def add_memories_batch(
        self,
        texts: list[tuple[str, dict[str, Any] | None]],
        progress_callback: Any = None
    ) -> None:
        """批量添加记忆

        Args:
            texts: (text, metadata) 元组列表
            progress_callback: 进度回调 (current, total)
        """
        if not self._enable_cache:
            # 不使用缓存，逐个添加
            for text, meta in texts:
                self.add_memory(text, meta)
            return

        # 使用批量嵌入生成
        text_list = [text for text, _ in texts]

        def embed_progress(current: int, total: int) -> None:
            if progress_callback:
                progress_callback(current, total)

        embeddings_dict = self._batch_embedding.embed_batch(
            text_list,
            use_cache=True,
            progress_callback=embed_progress
        )

        # 添加到数据库
        for (text, meta), embedding in zip(texts, embeddings_dict.values()):
            if not embedding:
                continue

            if self._collection is not None:
                mid = str(uuid4())
                self._collection.add(
                    ids=[mid],
                    documents=[text],
                    embeddings=[embedding],
                    metadatas=[meta or {}],
                )
            else:
                self._fallback.append({
                    "id": str(uuid4()),
                    "text": text,
                    "meta": meta or {}
                })

        # 清理降级列表
        if len(self._fallback) > 500:
            self._fallback = self._fallback[-400:]

    def get_cache_stats(self) -> dict[str, Any]:
        """获取缓存统计"""
        if not self._enable_cache:
            return {"cache_enabled": False}

        from engine.performance_cache import get_all_cache_stats
        stats = get_all_cache_stats()
        stats["cache_enabled"] = True
        return stats

    def clear_cache(self) -> None:
        """清空缓存"""
        if not self._enable_cache:
            return

        MEMORY_QUERY_CACHE.clear()
        EMBEDDING_CACHE.clear()
        logger.info("记忆缓存已清空")


# 为了向后兼容，保留原始的 MemoryManager 类
class MemoryManager(CachedMemoryManager):
    """原始的 MemoryManager（继承自 CachedMemoryManager）"""
    pass


_shared_memory: MemoryManager | None = None


def shared_memory_manager() -> MemoryManager:
    """進程內單例：避免每個引擎各建一套 Chroma PersistentClient。"""
    global _shared_memory
    if _shared_memory is None:
        _shared_memory = MemoryManager()
    return _shared_memory


def reset_shared_memory_manager() -> None:
    """測試用：還原單例。"""
    global _shared_memory
    _shared_memory = None
