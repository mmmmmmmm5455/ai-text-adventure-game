"""
批量查询优化
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar
from loguru import logger
import time

T = TypeVar('T')


class BatchProcessor:
    """批量查询处理器"""

    def __init__(
        self,
        batch_size: int = 10,
        timeout_ms: int = 5000,
        parallel: bool = False
    ):
        self._batch_size = batch_size
        self._timeout_ms = timeout_ms
        self._parallel = parallel

    def process_batch(
        self,
        items: list[T],
        process_func: Callable[[T], Any],
        progress_callback: Callable[[int, int], None] | None = None
    ) -> list[Any]:
        """批量处理项目

        Args:
            items: 要处理的项目列表
            process_func: 处理函数
            progress_callback: 进度回调 (current, total)

        Returns:
            处理结果列表
        """
        results = []
        total = len(items)

        # 分批处理
        for i in range(0, total, self._batch_size):
            batch = items[i:i + self._batch_size]

            if self._parallel:
                # 并行处理（未来可以扩展）
                batch_results = self._process_batch_parallel(batch, process_func)
            else:
                # 顺序处理
                batch_results = self._process_batch_sequential(batch, process_func)

            results.extend(batch_results)

            # 进度回调
            if progress_callback:
                progress_callback(min(i + self._batch_size, total), total)

        return results

    def _process_batch_sequential(
        self,
        batch: list[T],
        process_func: Callable[[T], Any]
    ) -> list[Any]:
        """顺序处理一批项目"""
        results = []
        for item in batch:
            try:
                result = process_func(item)
                results.append(result)
            except Exception as e:
                logger.error(f"处理项目失败: {e}")
                results.append(None)
        return results

    def _process_batch_parallel(
        self,
        batch: list[T],
        process_func: Callable[[T], Any]
    ) -> list[Any]:
        """并行处理一批项目（待实现）"""
        # 未来可以使用 concurrent.futures 或 asyncio
        return self._process_batch_sequential(batch, process_func)


class BatchMemoryQuery:
    """批量记忆查询"""

    def __init__(self, memory_manager):
        self._memory = memory_manager
        self._processor = BatchProcessor(batch_size=5)

    def query_batch(
        self,
        queries: list[str],
        k: int = 4,
        use_cache: bool = True
    ) -> dict[str, list[str]]:
        """批量查询记忆

        Args:
            queries: 查询列表
            k: 返回结果数量
            use_cache: 是否使用缓存

        Returns:
            查询结果字典 {query: [results]}
        """
        from engine.performance_cache import (
            MEMORY_QUERY_CACHE,
            make_memory_query_key,
            get_all_cache_stats
        )

        results = {}

        # 先从缓存获取
        if use_cache:
            for query in queries:
                key = make_memory_query_key(query, k)
                cached = MEMORY_QUERY_CACHE.get(key)
                if cached is not None:
                    results[query] = cached

        # 找出需要查询的项目
        missing_queries = [q for q in queries if q not in results]

        if missing_queries:
            # 批量查询
            def process_query(query: str) -> list[str]:
                return self._memory.query_relevant(query, k)

            batch_results = self._processor.process_batch(
                missing_queries,
                process_query
            )

            # 存储结果到缓存
            for query, result in zip(missing_queries, batch_results):
                results[query] = result

                if use_cache and result:
                    key = make_memory_query_key(query, k)
                    MEMORY_QUERY_CACHE.set(key, result)

        return results


class BatchEmbedding:
    """批量嵌入生成"""

    def __init__(self, embed_func: Callable[[str], list[float] | None]):
        self._embed_func = embed_func
        self._processor = BatchProcessor(batch_size=8)

    def embed_batch(
        self,
        texts: list[str],
        use_cache: bool = True,
        progress_callback: Callable[[int, int], None] | None = None
    ) -> dict[str, list[float] | None]:
        """批量生成嵌入

        Args:
            texts: 文本列表
            use_cache: 是否使用缓存
            progress_callback: 进度回调

        Returns:
            嵌入字典 {text: embedding}
        """
        from engine.performance_cache import (
            EMBEDDING_CACHE,
            make_embedding_key
        )

        results = {}

        # 先从缓存获取
        if use_cache:
            for text in texts:
                key = make_embedding_key(text)
                cached = EMBEDDING_CACHE.get(key)
                if cached is not None:
                    results[text] = cached

        # 找出需要生成的项目
        missing_texts = [t for t in texts if t not in results]

        if missing_texts:
            # 批量生成
            def embed_text(text: str) -> list[float] | None:
                return self._embed_func(text)

            batch_results = self._processor.process_batch(
                missing_texts,
                embed_text,
                progress_callback
            )

            # 存储结果到缓存
            for text, embedding in zip(missing_texts, batch_results):
                results[text] = embedding

                if use_cache and embedding:
                    key = make_embedding_key(text)
                    EMBEDDING_CACHE.set(key, embedding)

        return results


def performance_monitor(func: Callable):
    """性能监控装饰器"""
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.debug(f"{func.__name__} 执行时间: {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"{func.__name__} 失败 ({elapsed:.3f}s): {e}")
            raise
    return wrapper
