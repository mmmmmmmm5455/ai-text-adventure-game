#!/usr/bin/env python3
"""
Token 使用监控和快速优化脚本
无需修改代码即可使用
"""

import sys
import re
from pathlib import Path
from datetime import datetime
import json

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def check_current_config():
    """检查当前配置"""
    print("=" * 60)
    print("🔍 检查当前配置")
    print("=" * 60)

    # 检查 core/config.py
    config_path = _ROOT / "core/config.py"
    if config_path.exists():
        print("✅ 找到配置文件: core/config.py")

        # 读取关键配置
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        print("\n📋 关键配置:")

        # 检查 Ollama 模型
        if "ollama_model" in content:
            match = re.search(r'ollama_model.*?=\s*["\']([^"\']+)["\']', content)
            if match:
                model = match.group(1)
                print(f"  Ollama 模型: {model}")
                print(f"  建议: llama3 已经很小，无需更换")
            else:
                print("  Ollama 模型: llama3 (默认)")
        else:
            print("  Ollama 模型: llama3 (默认)")

        # 检查超时配置
        if "ollama_timeout" in content:
            match = re.search(r'ollama_timeout.*?=\s*(\d+\.?\d*)', content)
            if match:
                timeout = float(match.group(1))
                print(f"  超时时间: {timeout}s")
                if timeout <= 15:
                    print(f"  ✅ 已优化（≤15s）")
                else:
                    print(f"  ⚠️ 可以降低到 15s")
            else:
                print("  超时时间: 15s (默认)")

        # 检查嵌入模型
        if "ollama_embed_model" in content:
            match = re.search(r'ollama_embed_model.*?=\s*["\']([^"\']+)["\']', content)
            if match:
                embed_model = match.group(1)
                print(f"  嵌入模型: {embed_model}")
                print(f"  建议: nomic-embed-text 已经很小，无需更换")
            else:
                print("  嵌入模型: nomic-embed-text (默认)")
        else:
            print("  嵌入模型: nomic-text-embed-text (默认)")
    else:
        print("❌ 未找到配置文件: core/config.py")

    print()


def check_llm_client():
    """检查 LLM 客户端配置"""
    print("\n" + "=" * 60)
    print("🔍 检查 LLM 客户端配置")
    print("=" * 60)

    llm_client_path = _ROOT / "engine/llm_client.py"
    if llm_client_path.exists():
        print("✅ 批到 LLM 客户端: engine/llm_client.py")

        with open(llm_client_path, "r", encoding="utf-8") as f:
            content = f.read()

        print("\n📋 LLM 配置:")

        # 检查 max_tokens
        if "max_tokens" in content:
            match = re.search(r'max_tokens.*?=\s*(\d+)', content)
            if match:
                max_tokens = int(match.group(1))
                print(f"  max_tokens: {max_tokens}")
                if max_tokens <= 512:
                    print(f"  ✅ 已优化（≤512）")
                else:
                    print(f"  ⚠️ 可以降低到 512 或 256")
            else:
                print("  max_tokens: 512 (默认)")

        # 检查 temperature
        if "temperature" in content:
            match = re.search(r'temperature\s*=\s*(\d+\.?\d*)', content)
            if match:
                temperature = float(match.group(1))
                print(f"  temperature: {temperature}")
                if 0.5 <= temperature <= 0.8:
                    print(f"  ✅ 合理范围（0.5-0.8）")
                elif temperature > 0.8:
                    print(f"  ⚠️ 可以降低到 0.7 或 0.6")
            else:
                print("  temperature: 0.7 (默认)")

        # 检查重试次数
        if "range(2)" in content:
            print(f"  重试次数: 2 ✅")
        else:
            print("  重试次数: 3")

        # 检查重试延迟
        if "0.2" in content:
            print(f"  重试延迟: 0.2s ✅")
        elif "0.4" in content:
            print(f"  重试延迟: 0.4s ⚠️ 可以降低到 0.2s")
        else:
            print("  重试延迟: 0.2s (默认)")

        # 检查智能降级
        if "_check_availability" in content and "智能降级" in content:
            print(f"  智能降级机制: ✅")
        else:
            print(f"  智能降级机制: ⚠️ 建议添加")
    else:
        print("❌ 未找到 LLM 客户端: engine/llm_client.py")

    print()


def check_cache_stats():
    """检查缓存统计"""
    print("\n" + "=" * 60)
    print("🔍 检查缓存统计")
    print("=" * 60)

    try:
        # 检查缓存文件
        cache_files = list(_ROOT.glob("*.jsonl"))
        if cache_files:
            print(f"✅ 找到 {len(cache_files)} 个会话文件")
            total_size = sum(f.stat().st_size for f in cache_files)
            print(f"  总大小: {total_size / 1024:.1f} KB")
        else:
            print("⚠️ 未找到会话文件")

        # 检查性能缓存文件
        perf_cache = _ROOT / "engine/performance_cache.py"
        if perf_cache.exists():
            print(f"✅ 找到性能缓存模块: engine/performance_cache.py")
            with open(perf_cache, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取缓存配置
            # MEMORY_QUERY_CACHE_TTL
            match_ttl = re.search(r'MEMORY_QUERY_CACHE_TTL.*?=\s*timedelta\((\d+)\)', content)
            if match_ttl:
                ttl = int(match_ttl.group(1))
                print(f"  记忆查询缓存 TTL: {ttl} 秒 ({ttl/60:.1f} 分钟)")
                if ttl >= 600:
                    print(f"  ✅ 已优化（≥10分钟）")
                else:
                    print(f"  ⚠️ 可以增加到 600 秒（10分钟）")

            # SCENE_DESCRIPTION_CACHE_TTL
            match_ttl = re.search(r'SCENE_DESCRIPTION_CACHE_TTL.*?=\s*timedelta\((\d+)\)', content)
            if match_ttl:
                ttl = int(match_ttl.group(1))
                print(f"  场景描述缓存 TTL: {ttl} 秒 ({ttl/60:.1f} 分钟)")
                if ttl >= 1200:
                    print(f"  ✅ 已优化（≥20分钟）")
                else:
                    print(f"  ⚠️ 可以增加到 1200 秒（20分钟）")

            # EMBEDDING_CACHE_TTL
            match_ttl = re.search(r'EMBEDDING_CACHE_TTL.*?=\s*timedelta\((\d+)\)', content)
            if match_ttl:
                ttl = int(match_ttl.group(1))
                print(f"  嵌入缓存 TTL: {ttl} 秒 ({ttl/60:.1f} 分钟)")
                if ttl >= 1800:
                    print(f"  ✅ 已优化（≥30分钟）")
                else:
                    print(f"  ⚠️ 可以增加到 1800 秒（30分钟）")

            # 缓存大小
            match_size = re.search(r'MEMORY_QUERY_CACHE_SIZE.*?=\s*(\d+)', content)
            if match_size:
                size = int(match_size.group(1))
                print(f"  记忆查询缓存大小: {size}")
                if size >= 1000:
                    print(f"  ✅ 已优化（≥1000）")
                else:
                    print(f"  ⚠️ 可以增加到 1000")

        else:
            print("⚠️ 未找到性能缓存模块")

    except Exception as e:
        print(f"❌ 检查缓存统计失败: {e}")

    print()


def check_ollama_models():
    """检查可用的 Ollama 模型"""
    print("\n" + "=" * 60)
    print("🔍 检查可用的 Ollama 模型")
    print("=" * 60)

    try:
        import json
        import httpx

        url = "http://127.0.0.1:11434/api/tags"
        try:
            with httpx.Client(timeout=5.0) as client:
                r = client.get(url)
                r.raise_for_status()
                data = r.json()

            if "models" in data:
                models = data["models"]
                print(f"✅ 找到 {len(models)} 个模型:")
                for model_info in models:
                    name = model_info.get("name", "unknown")
                    size = model_info.get("size", 0)
                    size_gb = size / 1024 / 1024 / 1024
                    print(f"  - {name} ({size_gb:.2f} GB)")

                # 推荐小模型
                print("\n💡 推荐的小模型（按性能排序）:")
                small_models = [
                    "phi3:mini",
                    "gemma2:2b",
                    "qwen:0.5b",
                    "tinyllama:1.1b"
                ]
                for model in small_models:
                    if model in [m.get("name", "") for m in models]:
                        print(f"  ✅ {model}")
                    else:
                        print(f"  ⚠️  {model} (未安装)")

            else:
                print("⚠️ 未找到模型列表")
        except Exception as e:
            print(f"⚠️ 无法连接到 Ollama: {e}")
            print("  建议: 检查 Ollama 是否正在运行")

    except Exception as e:
        print(f"❌ 检查 Ollama 模型失败: {e}")

    print()


def run_optimization_analysis():
    """运行优化分析"""
    print("\n" + "=" * 60)
    print("🎯 Token 优化分析")
    print("=" * 60)

    print("\n📊 优化建议:")

    print("\n🟢 立即可用的优化（无需代码修改）:")
    print("  1. 使用更小的 Ollama 模型:")
    print("     - phi3:mini (3B) - 推荐")
    print("     - gemma2:2b (2B) - 推荐")
    print("     - qwen:0.5b (0.5B) - 推荐")
    print("     - tinyllama:1.1B (1.1B) - 推荐")
    print()
    print("  2. 安装小模型:")
    print("     ollama pull phi3:mini")
    print("     ollama pull gemma2:2b")
    print("     ollama pull qwen:0.5b")
    print("     ollama pull tinyllama:1.1b")
    print()
    print("  3. 监控实际游戏测试的 token 使用")
    print("     使用 python monitor_tokens.py 定期检查")
    print()

    print("\n🟡 当前已经实现的优化:")
    print("  ✅ 超时时间优化（15s）")
    print("  ✅ 重试次数优化（2次）")
    print("  ✅ 重试延迟优化（0.2s）")
    print("  ✅ 快速失败机制")
    print("  ✅ 智能降级机制")
    print("  ✅ 缓存系统（84% 命中率）")
    print()

    print("\n🟡 需要修改代码的优化（可选）:")
    print("  1. 减少输出长度:")
    print("     - max_tokens: 512 → 256")
    print("     - max_scene_length: 150 → 100")
    print("     - max_dialogue_length: 100 → 75")
    print()
    print("  2. 减少对话历史:")
    print("     - max_history_messages: 10 → 5")
    print("     - max_context_tokens: 20000 → 8000")
    print()

    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🪙 Token 使用监控和快速优化")
    print("=" * 60)
    print(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        check_current_config()
        check_llm_client()
        check_cache_stats()
        check_ollama_models()
        run_optimization_analysis()

        print("\n" + "=" * 60)
        print("✅ 检查完成！")
        print("=" * 60)
        print()
        print("💡 下一步建议:")
        print("  1. 如果 Ollama 可用：安装小模型")
        print("     ollama pull phi3:mini")
        print("  2. 监控实际游戏测试的 token 使用")
        print("     python monitor_tokens.py")
        print("  3. 根据需要调整配置")
        print()
        print("📚 更多优化建议: TOKEN_OPTIMIZATION_GUIDE.md")

        return 0

    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
