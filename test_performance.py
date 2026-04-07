#!/usr/bin/env python
"""性能优化测试脚本"""

import time
from engine.llm_client import LLMClient

def test_performance():
    """测试性能改进"""
    print("🧪 性能优化测试")
    print("=" * 50)

    llm = LLMClient()

    # 测试 1：生成文本
    print("\n📝 测试 1：生成文本")
    start = time.time()
    result = llm.generate_text("测试生成", system="测试系统")
    elapsed = time.time() - start

    print(f"响应时间: {elapsed:.2f} 秒")
    print(f"结果长度: {len(result)} 字符")
    print(f"结果: {result[:100]}...")

    # 测试 2：生成多个文本
    print("\n📝 测试 2：批量生成（10 次）")
    total_time = 0
    for i in range(10):
        start = time.time()
        result = llm.generate_text(f"测试生成 {i}", system="测试系统")
        elapsed = time.time() - start
        total_time += elapsed
        print(f"  第 {i+1} 次: {elapsed:.2f} 秒")

    avg_time = total_time / 10
    print(f"平均响应时间: {avg_time:.2f} 秒")

    # 测试 3：健康检查
    print("\n🔍 测试 3：健康检查")
    start = time.time()
    available = llm.health_check()
    elapsed = time.time() - start

    print(f"Ollama 可用: {available}")
    print(f"检查时间: {elapsed:.2f} 秒")

    # 测试 4：智能降级
    print("\n📉 测试 4：智能降级（缓存健康状态）")
    # 第一次检查
    start = time.time()
    available = llm._check_availability()
    elapsed1 = time.time() - start
    print(f"第一次检查: {elapsed1:.2f} 秒")

    # 第二次检查（应该使用缓存）
    start = time.time()
    available = llm._check_availability()
    elapsed2 = time.time() - start
    print(f"第二次检查（缓存）: {elapsed2:.2f} 秒")
    print(f"缓存效果: {((elapsed1 - elapsed2) / elapsed1 * 100):.1f}% 提升")

    print("\n✅ 测试完成！")

if __name__ == "__main__":
    test_performance()
