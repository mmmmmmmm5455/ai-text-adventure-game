"""
性能优化模块：缓存机制和批量查询
"""

from __future__ import annotations

from typing import Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
from loguru import logger


@dataclass
class CacheEntry:
    """缓存条目"""
    value: Any
    created_at: datetime
    ttl: timedelta
    hit_count: int = 0

    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.now() - self.created_at > self.ttl

    def hit(self) -> None:
        """记录命中"""
        self.hit_count += 1


@dataclass
class CacheStats:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    size: int = 0

    @property
    def hit_rate(self) -> float:
        """命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def reset(self) -> None:
        """重置统计"""
        self.hits = 0
        self.misses = 0
        self.size = 0


class TTLCache:
    """带 TTL 的缓存系统"""

    def __init__(
        self,
        default_ttl: timedelta = timedelta(minutes=5),
        max_size: int = 1000,
        name: str = "cache"
    ):
        self._cache: dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._name = name
        self._stats = CacheStats()

    def _make_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""
        # 使用函数名 + 参数哈希作为键
        key_parts = [
            func.__name__,
            str(args),
            str(sorted(kwargs.items()))
        ]
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Any | None:
        """获取缓存值"""
        if key not in self._cache:
            self._stats.misses += 1
            return None

        entry = self._cache[key]

        # 检查是否过期
        if entry.is_expired():
            del self._cache[key]
            self._stats.size -= 1
            self._stats.misses += 1
            return None

        # 命中缓存
        entry.hit()
        self._stats.hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: timedelta | None = None) -> None:
        """设置缓存值"""
        # 检查缓存大小
        if len(self._cache) >= self._max_size:
            # 删除最旧的条目
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].created_at
            )
            del self._cache[oldest_key]
            self._stats.size -= 1

        # 添加新条目
        ttl = ttl or self._default_ttl
        entry = CacheEntry(
            value=value,
            created_at=datetime.now(),
            ttl=ttl,
            hit_count=0
        )
        self._cache[key] = entry
        self._stats.size += 1

    def invalidate(self, key: str) -> bool:
        """使缓存失效"""
        if key in self._cache:
            del self._cache[key]
            self._stats.size -= 1
            return True
        return False

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._stats.size = 0

    def cleanup_expired(self) -> int:
        """清理过期条目"""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]

        for key in expired_keys:
            del self._cache[key]
            self._stats.size -= len(expired_keys)

        return len(expired_keys)

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计"""
        return {
            "name": self._name,
            "hits": self._stats.hits,
            "misses": self._stats.misses,
            "size": self._stats.size,
            "hit_rate": f"{self._stats.hit_rate:.2%}",
        }

    def reset_stats(self) -> None:
        """重置统计"""
        self._stats.reset()


def cached(
    cache: TTLCache,
    ttl: timedelta | None = None,
    key_func: Callable | None = None
):
    """缓存装饰器

    Args:
        cache: 缓存实例
        ttl: TTL 时间（覆盖默认值）
        key_func: 自定义键生成函数
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = cache._make_key(func, args, kwargs)

            # 尝试从缓存获取
            value = cache.get(key)
            if value is not None:
                return value

            # 缓存未命中，调用函数
            result = func(*args, **kwargs)

            # 存入缓存
            cache.set(key, result, ttl)

            return result

        return wrapper
    return decorator


# 全局缓存实例
MEMORY_QUERY_CACHE = TTLCache(
    default_ttl=timedelta(minutes=5),
    max_size=500,
    name="memory_query_cache"
)

SCENE_DESCRIPTION_CACHE = TTLCache(
    default_ttl=timedelta(minutes=10),
    max_size=100,
    name="scene_description_cache"
)

DIALOGUE_CACHE = TTLCache(
    default_ttl=timedelta(minutes=3),
    max_size=200,
    name="dialogue_cache"
)

EMBEDDING_CACHE = TTLCache(
    default_ttl=timedelta(minutes=30),
    max_size=1000,
    name="embedding_cache"
)


def get_all_cache_stats() -> dict[str, dict[str, Any]]:
    """获取所有缓存的统计"""
    return {
        "memory_query": MEMORY_QUERY_CACHE.get_stats(),
        "scene_description": SCENE_DESCRIPTION_CACHE.get_stats(),
        "dialogue": DIALOGUE_CACHE.get_stats(),
        "embedding": EMBEDDING_CACHE.get_stats(),
    }


def cleanup_all_caches() -> dict[str, int]:
    """清理所有缓存"""
    return {
        "memory_query": MEMORY_QUERY_CACHE.cleanup_expired(),
        "scene_description": SCENE_DESCRIPTION_CACHE.cleanup_expired(),
        "dialogue": DIALOGUE_CACHE.cleanup_expired(),
        "embedding": EMBEDDING_CACHE.cleanup_expired(),
    }


def clear_all_caches() -> None:
    """清空所有缓存"""
    MEMORY_QUERY_CACHE.clear()
    SCENE_DESCRIPTION_CACHE.clear()
    DIALOGUE_CACHE.clear()
    EMBEDDING_CACHE.clear()
    logger.info("所有缓存已清空")


def make_memory_query_key(query: str, k: int) -> str:
    """生成记忆查询缓存键"""
    return f"query:{query}:{k}"


def make_scene_description_key(scene_id: str, time_label: str) -> str:
    """生成场景描述缓存键"""
    return f"scene:{scene_id}:{time_label}"


def make_dialogue_key(scene_id: str, npc_id: str, dialogue_round: int) -> str:
    """生成对话缓存键"""
    return f"dialogue:{scene_id}:{npc_id}:{dialogue_round}"


def make_embedding_key(text: str) -> str:
    """生成嵌入缓存键"""
    # 使用文本的 MD5 哈希作为键
    return hashlib.md5(text.encode()).hexdigest()
