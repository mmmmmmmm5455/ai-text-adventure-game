"""
测试性能优化功能（缓存和批量查询）
"""

import sys
from pathlib import Path
from datetime import timedelta
import time

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from engine.performance_cache import (
    TTLCache,
    CacheEntry,
    cached,
    MEMORY_QUERY_CACHE,
    SCENE_DESCRIPTION_CACHE,
    DIALOGUE_CACHE,
    EMBEDDING_CACHE,
    make_memory_query_key,
    make_scene_description_key,
    make_dialogue_key,
    make_embedding_key,
    get_all_cache_stats,
    cleanup_all_caches,
    clear_all_caches,
)


def test_ttl_cache():
    """测试 TTL 缓存"""
    print("=" * 60)
    print("测试 1: TTL 缓存基本功能")
    print("=" * 60)

    cache = TTLCache(
        default_ttl=timedelta(seconds=2),
        max_size=10,
        name="test_cache"
    )

    # 设置值
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    print(f"✓ 设置缓存值")
    print(f"  key1 = {cache.get('key1')}")
    print(f"  key2 = {cache.get('key2')}")

    # 获取值
    value1 = cache.get("key1")
    assert value1 == "value1"
    print(f"✓ 获取缓存值")
    print(f"  获取 key1: {value1}")

    # 缓存未命中
    value3 = cache.get("key3")
    assert value3 is None
    print(f"✓ 缓存未命中")
    print(f"  获取 key3: {value3}")

    # TTL 过期
    time.sleep(2.1)
    value1_expired = cache.get("key1")
    assert value1_expired is None
    print(f"✓ TTL 过期")
    print(f"  过期后获取 key1: {value1_expired}")

    # 缓存统计
    stats = cache.get_stats()
    print(f"✓ 缓存统计")
    print(f"  命中次数: {stats['hits']}")
    print(f"  未命中次数: {stats['misses']}")
    print(f"  当前大小: {stats['size']}")
    print(f"  命中率: {stats['hit_rate']}")

    print()


def test_cached_decorator():
    """测试缓存装饰器"""
    print("=" * 60)
    print("测试 2: 缓存装饰器")
    print("=" * 60)

    cache = TTLCache(
        default_ttl=timedelta(seconds=5),
        max_size=10,
        name="decorator_test"
    )

    call_count = 0

    @cached(cache)
    def expensive_function(x: int) -> int:
        nonlocal call_count
        call_count += 1
        time.sleep(0.1)  # 模拟耗时操作
        return x * x

    # 第一次调用
    start = time.time()
    result1 = expensive_function(5)
    elapsed1 = time.time() - start
    print(f"✓ 第一次调用")
    print(f"  结果: {result1}, 耗时: {elapsed1:.3f}s, 调用次数: {call_count}")

    # 第二次调用（应该从缓存获取）
    start = time.time()
    result2 = expensive_function(5)
    elapsed2 = time.time() - start
    print(f"✓ 第二次调用（缓存命中）")
    print(f"  结果: {result2}, 耗时: {elapsed2:.3f}s, 调用次数: {call_count}")

    assert call_count == 1, "应该只调用一次"
    assert elapsed2 < elapsed1, "缓存命中应该更快"

    print()


def test_cache_stats():
    """测试缓存统计"""
    print("=" * 60)
    print("测试 3: 缓存统计")
    print("=" * 60)

    cache = TTLCache(
        default_ttl=timedelta(minutes=5),
        max_size=10,
        name="stats_test"
    )

    # 重置统计
    cache.reset_stats()

    # 生成一些缓存命中和未命中
    cache.set("key1", "value1")
    cache.get("key1")  # 命中
    cache.get("key1")  # 命中
    cache.get("key2")  # 未命中
    cache.get("key2")  # 未命中

    stats = cache.get_stats()
    print(f"✓ 缓存统计")
    print(f"  命中次数: {stats['hits']}")
    print(f"  未命中次数: {stats['misses']}")
    print(f"  命中率: {stats['hit_rate']}")

    assert stats['hits'] == 2, f"预期 2 次命中，实际 {stats['hits']} 次"
    assert stats['misses'] == 2, f"预期 2 次未命中，实际 {stats['misses']} 次"
    # hit_rate 是字符串格式，转换为浮点数
    hit_rate_value = float(stats['hit_rate'].rstrip('%')) / 100.0
    assert abs(hit_rate_value - 0.5) < 0.01, f"预期命中率 0.5，实际 {hit_rate_value}"

    print()


def test_cache_size_limit():
    """测试缓存大小限制"""
    print("=" * 60)
    print("测试 4: 缓存大小限制")
    print("=" * 60)

    cache = TTLCache(
        default_ttl=timedelta(minutes=5),
        max_size=5,
        name="size_test"
    )

    # 添加 10 个条目（超过 max_size）
    for i in range(10):
        cache.set(f"key{i}", f"value{i}")

    stats = cache.get_stats()
    print(f"✓ 添加 10 个条目后")
    print(f"  当前大小: {stats['size']}")
    print(f"  预期大小: 5")

    assert stats['size'] <= 5, "缓存大小不应超过 max_size"

    # 检查最旧的键是否被删除
    oldest_key = cache.get("key0")
    print(f"  最旧的键 (key0): {oldest_key}")
    assert oldest_key is None, "最旧的键应该被删除"

    # 检查最新的键是否存在
    newest_key = cache.get("key9")
    print(f"  最新的键 (key9): {newest_key}")
    assert newest_key is not None, "最新的键应该存在"

    print()


def test_key_generation():
    """测试键生成函数"""
    print("=" * 60)
    print("测试 5: 键生成函数")
    print("=" * 60)

    # 记忆查询键
    key1 = make_memory_query_key("测试查询", 4)
    key2 = make_memory_query_key("测试查询", 4)
    key3 = make_memory_query_key("测试查询", 5)

    print(f"✓ 记忆查询键")
    print(f"  相同查询+k=4: {key1 == key2}")
    print(f"  相同查询+k=5: {key1 == key3}")

    assert key1 == key2, "相同参数应该生成相同的键"
    assert key1 != key3, "不同参数应该生成不同的键"

    # 场景描述键
    scene_key = make_scene_description_key("village_square", "day")
    print(f"✓ 场景描述键")
    print(f"  场景键: {scene_key[:20]}...")

    # 对话键
    dialogue_key = make_dialogue_key("village_square", "npc_001", 1)
    print(f"✓ 对话键")
    print(f"  对话键: {dialogue_key[:20]}...")

    # 嵌入键
    text = "这是一段测试文本"
    embed_key = make_embedding_key(text)
    print(f"✓ 嵌入键")
    print(f"  文本: {text}")
    print(f"  嵌入键: {embed_key[:20]}...")

    print()


def test_global_caches():
    """测试全局缓存"""
    print("=" * 60)
    print("测试 6: 全局缓存")
    print("=" * 60)

    # 向全局缓存添加数据
    MEMORY_QUERY_CACHE.set("test_query", ["result1", "result2"])
    SCENE_DESCRIPTION_CACHE.set("test_scene", "这是场景描述")
    DIALOGUE_CACHE.set("test_dialogue", "这是对话内容")
    EMBEDDING_CACHE.set("test_text", [0.1, 0.2, 0.3])

    # 获取所有缓存统计
    all_stats = get_all_cache_stats()
    print(f"✓ 所有缓存统计")
    for cache_name, stats in all_stats.items():
        print(f"  {cache_name}:")
        print(f"    命中率: {stats['hit_rate']}")
        print(f"    大小: {stats['size']}")

    # 清理过期缓存
    cleaned = cleanup_all_caches()
    print(f"✓ 清理过期缓存")
    print(f"  清理数量: {cleaned}")

    # 清空所有缓存
    clear_all_caches()
    print(f"✓ 清空所有缓存")

    all_stats_after = get_all_cache_stats()
    for cache_name, stats in all_stats_after.items():
        assert stats['size'] == 0, f"{cache_name} 应该被清空"

    print()


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("性能优化功能测试（缓存和批量查询）")
    print("=" * 60 + "\n")

    try:
        test_ttl_cache()
        test_cached_decorator()
        test_cache_stats()
        test_cache_size_limit()
        test_key_generation()
        test_global_caches()

        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        return True

    except AssertionError as e:
        print("=" * 60)
        print(f"❌ 测试失败: {e}")
        print("=" * 60)
        return False
    except Exception as e:
        print("=" * 60)
        print(f"❌ 测试出错: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
