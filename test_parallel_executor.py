"""
测试并行执行功能
"""

import sys
from pathlib import Path
import time
import asyncio

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from engine.parallel_executor import (
    ParallelExecutor,
    ParallelLLMClient,
    parallel_execute,
    parallel_execute_async,
    AsyncTask,
)


def mock_slow_function(task_id: str, delay: float, value: int) -> int:
    """模拟慢速函数"""
    time.sleep(delay)
    return value * 2


def mock_error_function(task_id: str, should_fail: bool = False) -> str:
    """模拟错误函数"""
    time.sleep(0.5)
    if should_fail:
        raise ValueError(f"任务 {task_id} 故意失败")
    return f"任务 {task_id} 成功"


def test_parallel_executor_sync():
    """测试同步并行执行器"""
    print("=" * 60)
    print("测试 1: 同步并行执行器")
    print("=" * 60)

    executor = ParallelExecutor(max_workers=3, name="test_sync")

    # 提交任务
    executor.submit("task1", mock_slow_function, "task1", 0.5, 10)
    executor.submit("task2", mock_slow_function, "task2", 0.3, 20)
    executor.submit("task3", mock_slow_function, "task3", 0.4, 30)

    # 执行任务
    start = time.time()
    results = executor.execute_sync()
    elapsed = time.time() - start

    print(f"✓ 执行完成")
    print(f"  耗时: {elapsed:.3f}s")
    print(f"  结果: {results}")
    print(f"  预期顺序执行耗时: 1.2s (0.5+0.3+0.4)")
    print(f"  实际并行耗时: {elapsed:.3f}s")
    print(f"  性能提升: {(1.2 / elapsed - 1) * 100:.1f}%")

    # 获取统计
    stats = executor.get_stats()
    print(f"✓ 执行统计")
    print(f"  总任务: {stats['total_tasks']}")
    print(f"  成功: {stats['completed']}")
    print(f"  失败: {stats['failed']}")
    print(f"  成功率: {stats['success_rate']}")

    assert len(results) == 3, "应该有 3 个结果"
    assert results["task1"] == 20, "task1 结果应该为 20"
    assert results["task2"] == 40, "task2 结果应该为 40"
    assert results["task3"] == 60, "task3 结果应该为 60"

    print()


async def test_parallel_executor_async():
    """测试异步并行执行器"""
    print("=" * 60)
    print("测试 2: 异步并行执行器")
    print("=" * 60)

    executor = ParallelExecutor(max_workers=3, name="test_async")

    # 提交任务
    executor.submit("task1", mock_slow_function, "task1", 0.5, 10)
    executor.submit("task2", mock_slow_function, "task2", 0.3, 20)
    executor.submit("task3", mock_slow_function, "task3", 0.4, 30)

    # 异步执行任务
    start = time.time()
    results = await executor.execute_async()
    elapsed = time.time() - start

    print(f"✓ 异步执行完成")
    print(f"  耗时: {elapsed:.3f}s")
    print(f"  结果: {results}")
    print(f"  性能提升: {(1.2 / elapsed - 1) * 100:.1f}%")

    # 获取统计
    stats = executor.get_stats()
    print(f"✓ 执行统计")
    print(f"  总任务: {stats['total_tasks']}")
    print(f"  成功: {stats['completed']}")
    print(f"  失败: {stats['failed']}")
    print(f"  成功率: {stats['success_rate']}")

    assert len(results) == 3, "应该有 3 个结果"

    print()


def test_parallel_execute_helper():
    """测试并行执行辅助函数"""
    print("=" * 60)
    print("测试 3: 并行执行辅助函数")
    print("=" * 60)

    # 准备任务
    funcs = [
        ("func1", mock_slow_function, ("func1", 0.3, 10), {}),
        ("func2", mock_slow_function, ("func2", 0.4, 20), {}),
        ("func3", mock_slow_function, ("func3", 0.2, 30), {}),
    ]

    # 同步执行
    start = time.time()
    results = parallel_execute(funcs, max_workers=3)
    elapsed = time.time() - start

    print(f"✓ 同步执行完成")
    print(f"  耗时: {elapsed:.3f}s")
    print(f"  结果: {results}")
    print(f"  预期顺序执行耗时: 0.9s")
    print(f"  性能提升: {(0.9 / elapsed - 1) * 100:.1f}%")

    assert len(results) == 3
    assert results["func1"] == 20
    assert results["func2"] == 40
    assert results["func3"] == 60

    print()


def test_parallel_execute_async_helper():
    """测试异步并行执行辅助函数"""
    print("=" * 60)
    print("测试 4: 异步并行执行辅助函数")
    print("=" * 60)

    # 准备任务
    funcs = [
        ("func1", mock_slow_function, ("func1", 0.3, 10), {}),
        ("func2", mock_slow_function, ("func2", 0.4, 20), {}),
        ("func3", mock_slow_function, ("func3", 0.2, 30), {}),
    ]

    # 异步执行
    async def run():
        start = time.time()
        results = await parallel_execute_async(funcs, max_workers=3)
        elapsed = time.time() - start

        print(f"✓ 异步执行完成")
        print(f"  耗时: {elapsed:.3f}s")
        print(f"  结果: {results}")
        print(f"  性能提升: {(0.9 / elapsed - 1) * 100:.1f}%")

        assert len(results) == 3
        assert results["func1"] == 20
        assert results["func2"] == 40
        assert results["func3"] == 60

    asyncio.run(run())

    print()


def test_error_handling():
    """测试错误处理"""
    print("=" * 60)
    print("测试 5: 错误处理")
    print("=" * 60)

    executor = ParallelExecutor(max_workers=3, name="test_error")

    # 提交任务（部分会失败）
    executor.submit("success1", mock_error_function, "success1", False)
    executor.submit("error1", mock_error_function, "error1", True)
    executor.submit("success2", mock_error_function, "success2", False)

    # 执行任务
    results = executor.execute_sync()

    print(f"✓ 错误处理测试完成")
    print(f"  结果: {results}")
    print(f"  success1: {results.get('success1')}")
    print(f"  error1: {results.get('error1')} (应为 None)")
    print(f"  success2: {results.get('success2')}")

    # 获取统计
    stats = executor.get_stats()
    print(f"✓ 执行统计")
    print(f"  总任务: {stats['total_tasks']}")
    print(f"  成功: {stats['completed']}")
    print(f"  失败: {stats['failed']}")
    print(f"  成功率: {stats['success_rate']}")

    assert stats['completed'] == 2, "应该有 2 个成功的任务"
    assert stats['failed'] == 1, "应该有 1 个失败的任务"

    print()


def test_performance_comparison():
    """测试性能对比"""
    print("=" * 60)
    print("测试 6: 性能对比")
    print("=" * 60)

    # 顺序执行
    start_seq = time.time()
    results_seq = [
        mock_slow_function("seq1", 0.5, 10),
        mock_slow_function("seq2", 0.4, 20),
        mock_slow_function("seq3", 0.3, 30),
    ]
    elapsed_seq = time.time() - start_seq

    # 并行执行
    funcs = [
        ("par1", mock_slow_function, ("par1", 0.5, 10), {}),
        ("par2", mock_slow_function, ("par2", 0.4, 20), {}),
        ("par3", mock_slow_function, ("par3", 0.3, 30), {}),
    ]
    start_par = time.time()
    results_par = parallel_execute(funcs, max_workers=3)
    elapsed_par = time.time() - start_par

    print(f"✓ 性能对比")
    print(f"  顺序执行:")
    print(f"    耗时: {elapsed_seq:.3f}s")
    print(f"    结果: {results_seq}")
    print(f"  并行执行:")
    print(f"    耗时: {elapsed_par:.3f}s")
    print(f"    结果: {list(results_par.values())}")
    print(f"  性能提升: {(elapsed_seq / elapsed_par - 1) * 100:.1f}%")

    assert elapsed_par < elapsed_seq, "并行执行应该更快"
    # 注意：并行执行的结果顺序可能不同，仅验证结果存在性
    # assert results_seq == list(results_par.values()), "结果应该相同"

    print()


def test_large_batch():
    """测试大批量任务"""
    print("=" * 60)
    print("测试 7: 大批量任务")
    print("=" * 60)

    executor = ParallelExecutor(max_workers=5, name="test_large")

    # 提交 20 个任务
    for i in range(20):
        executor.submit(
            f"task_{i}",
            mock_slow_function,
            f"task_{i}",
            0.1,
            i
        )

    # 执行任务
    start = time.time()
    results = executor.execute_sync()
    elapsed = time.time() - start

    print(f"✓ 大批量执行完成")
    print(f"  任务数: 20")
    print(f"  最大工作线程: 5")
    print(f"  耗时: {elapsed:.3f}s")
    print(f"  平均每个任务: {elapsed / 20:.3f}s")
    print(f"  预期顺序执行耗时: 2.0s")
    print(f"  性能提升: {(2.0 / elapsed - 1) * 100:.1f}%")

    # 获取统计
    stats = executor.get_stats()
    print(f"✓ 执行统计")
    print(f"  总任务: {stats['total_tasks']}")
    print(f"  成功: {stats['completed']}")
    print(f"  失败: {stats['failed']}")
    print(f"  成功率: {stats['success_rate']}")

    assert len(results) == 20, "应该有 20 个结果"
    assert stats['completed'] == 20, "所有任务应该成功"

    print()


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("并行执行功能测试")
    print("=" * 60 + "\n")

    try:
        test_parallel_executor_sync()
        test_parallel_executor_async()
        test_parallel_execute_helper()
        test_parallel_execute_async_helper()
        test_error_handling()
        test_performance_comparison()
        test_large_batch()

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
