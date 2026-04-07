"""
测试批量查询功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from engine.batch_query import (
    BatchProcessor,
    BatchMemoryQuery,
    BatchEmbedding,
    performance_monitor,
)


class MockMemoryManager:
    """模拟的记忆管理器"""

    def __init__(self):
        self._memories = {
            "村庄": ["村庄描述1", "村庄描述2"],
            "森林": ["森林描述1", "森林描述2"],
            "旅店": ["旅店描述1", "旅店描述2"],
        }

    def query_relevant(self, query: str, k: int = 4) -> list[str]:
        """模拟查询"""
        for key, values in self._memories.items():
            if key in query:
                return values[:k]
        return []


class MockEmbeddingFunction:
    """模拟的嵌入函数"""

    def __call__(self, text: str) -> list[float] | None:
        """模拟嵌入生成"""
        # 使用简单的哈希值作为嵌入
        import hashlib
        hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [(hash_value % 100) / 100.0 for _ in range(10)]


def test_batch_processor():
    """测试批量处理器"""
    print("=" * 60)
    print("测试 1: 批量处理器")
    print("=" * 60)

    processor = BatchProcessor(batch_size=3)

    # 创建测试数据
    items = list(range(10))

    def process_func(x: int) -> int:
        return x * 2

    # 批量处理
    results = processor.process_batch(items, process_func)
    print(f"✓ 批量处理")
    print(f"  输入: {items}")
    print(f"  输出: {results}")
    print(f"  预期: {list(map(process_func, items))}")

    assert len(results) == len(items)
    assert results == list(map(process_func, items))

    # 测试进度回调
    progress_updates = []

    def progress_callback(current: int, total: int) -> None:
        progress_updates.append((current, total))

    results2 = processor.process_batch(items, process_func, progress_callback)
    print(f"✓ 进度回调")
    print(f"  进度更新次数: {len(progress_updates)}")
    print(f"  进度更新: {progress_updates}")

    assert len(progress_updates) > 0

    print()


def test_batch_memory_query():
    """测试批量记忆查询"""
    print("=" * 60)
    print("测试 2: 批量记忆查询")
    print("=" * 60)

    mock_memory = MockMemoryManager()
    batch_query = BatchMemoryQuery(mock_memory)

    # 创建查询列表
    queries = ["村庄", "森林", "旅店"]

    # 批量查询
    results = batch_query.query_batch(queries, k=2)
    print(f"✓ 批量查询")
    for query, result in results.items():
        print(f"  查询: {query}")
        print(f"  结果: {result}")

    assert len(results) == len(queries)
    assert "村庄" in results
    assert "森林" in results
    assert "旅店" in results

    print()


def test_batch_embedding():
    """测试批量嵌入生成"""
    print("=" * 60)
    print("测试 3: 批量嵌入生成")
    print("=" * 60)

    mock_embed = MockEmbeddingFunction()
    batch_embedding = BatchEmbedding(mock_embed)

    # 创建文本列表
    texts = ["文本1", "文本2", "文本3", "文本4", "文本5"]

    # 批量生成嵌入
    results = batch_embedding.embed_batch(texts, use_cache=False)
    print(f"✓ 批量生成嵌入")
    for text, embedding in results.items():
        print(f"  文本: {text}")
        print(f"  嵌入: {embedding[:3]}...")

    assert len(results) == len(texts)
    for text, embedding in results.items():
        assert embedding is not None
        assert len(embedding) == 10

    # 测试进度回调
    progress_updates = []

    def progress_callback(current: int, total: int) -> None:
        progress_updates.append((current, total))

    results2 = batch_embedding.embed_batch(
        texts,
        use_cache=False,
        progress_callback=progress_callback
    )
    print(f"✓ 进度回调")
    print(f"  进度更新次数: {len(progress_updates)}")

    assert len(progress_updates) > 0

    print()


def test_performance_monitor():
    """测试性能监控装饰器"""
    print("=" * 60)
    print("测试 4: 性能监控装饰器")
    print("=" * 60)

    @performance_monitor
    def fast_function():
        return 42

    @performance_monitor
    def slow_function():
        import time
        time.sleep(0.1)
        return 100

    # 测试快速函数
    result1 = fast_function()
    print(f"✓ 快速函数")
    print(f"  结果: {result1}")
    assert result1 == 42

    # 测试慢速函数
    result2 = slow_function()
    print(f"✓ 慢速函数")
    print(f"  结果: {result2}")
    assert result2 == 100

    print()


def test_batch_processor_with_errors():
    """测试批量处理器处理错误"""
    print("=" * 60)
    print("测试 5: 批量处理器处理错误")
    print("=" * 60)

    processor = BatchProcessor(batch_size=3)

    # 创建测试数据
    items = [1, 2, 3, 4, 5]

    def process_func(x: int) -> int:
        if x == 3:
            raise ValueError("测试错误")
        return x * 2

    # 批量处理（应该忽略错误）
    results = processor.process_batch(items, process_func)
    print(f"✓ 批量处理（带错误）")
    print(f"  输入: {items}")
    print(f"  输出: {results}")

    # 第 3 个元素（值为 3）应该返回 None
    assert results[2] is None
    # 其他元素应该正常处理
    assert results[0] == 2
    assert results[1] == 4
    assert results[3] == 8
    assert results[4] == 10

    print()


def test_batch_processor_large_dataset():
    """测试批量处理器处理大数据集"""
    print("=" * 60)
    print("测试 6: 批量处理器处理大数据集")
    print("=" * 60)

    processor = BatchProcessor(batch_size=100)

    # 创建大数据集
    items = list(range(1000))

    def process_func(x: int) -> int:
        return x * 2

    # 批量处理
    import time
    start = time.time()
    results = processor.process_batch(items, process_func)
    elapsed = time.time() - start

    print(f"✓ 批量处理大数据集")
    print(f"  数据集大小: {len(items)}")
    print(f"  批量大小: {processor._batch_size}")
    print(f"  耗时: {elapsed:.3f}s")

    assert len(results) == len(items)
    assert results == list(map(process_func, items))

    print()


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("批量查询功能测试")
    print("=" * 60 + "\n")

    try:
        test_batch_processor()
        test_batch_memory_query()
        test_batch_embedding()
        test_performance_monitor()
        test_batch_processor_with_errors()
        test_batch_processor_large_dataset()

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
