# 🪙 Token 使用优化指南

**目标：** 最小化 token 使用，避免浪费
**日期：** 2026年4月7日

---

## 📊 当前状态

**Session Status:**
- **模型：** coze/auto
- **Tokens:**
  - 输入（in）：29k
  - 输出（out）：11k
  - 总计：40k
- **缓存命中率：** 84% ✅（很好！）
- **上下文使用：** 158k/200k (79%)
- **成本：** $0.0000

---

## 🎯 Token 优化策略

### 1. 使用更高效的模型

**当前：** `coze/auto`（自动选择，可能不是最优）

**建议：**
```python
# 在 core/config.py 或环境变量中
# 使用更小的模型用于简单任务
MODEL_SMALL = "qwen-plus"  # 通义理解力强，成本低
MODEL_FAST = "gemma-7b"  # 速度快，token 少
MODEL_CHEAP = "phi-3-mini"  # 超低成本
```

### 2. 优化 Prompt 设计

**❌ 不好的做法：**
```python
prompt = """
请帮我分析以下内容，并给出详细的解释和建议：
[长篇大论...]
"""
```

**✅ 好的做法：**
```python
prompt = "分析文本：{text}。3个关键词。"
```

**原则：**
- 使用简洁的指令
- 避免冗余说明
- 限制输出长度
- 使用结构化格式（JSON）

### 3. 减少上下文

**问题：** 每次对话都携带完整上下文（158k/200k = 79%）

**解决方案：**
```python
# 1. 使用更短的对话历史
MAX_HISTORY_MESSAGES = 5  # 只保留最近 5 条消息
MAX_HISTORY_TOKENS = 10000  # 最多 10k tokens

# 2. 压缩上下文
COMPRESS_CONTEXT = True  # 启用上下文压缩

# 3. 动态调整上下文
if is_simple_task:
    MAX_HISTORY_MESSAGES = 2
else:
    MAX_HISTORY_MESSAGES = 10
```

### 4. 使用缓存系统

**当前缓存命中率：** 84% ✅（很好！）

**优化建议：**
```python
# 增加更多缓存
MEMORY_QUERY_CACHE_TTL = 600  # 从 300 秒 → 600 秒
SCENE_DESCRIPTION_CACHE_TTL = 1200  # 从 600 秒 → 1200 秒
EMBEDDING_CACHE_TTL = 1800  # 从 1800 秒 → 1800 秒
DIALOGUE_CACHE_TTL = 600  # 从 180 秒 → 600 秒

# 增加缓存大小
MEMORY_QUERY_CACHE_SIZE = 1000  # 从 500 → 1000
SCENE_DESCRIPTION_CACHE_SIZE = 200  # 从 100 → 200
EMBEDDING_CACHE_SIZE = 2000  # 从 1000 → 2000
```

### 5. 减少输出长度

**问题：** LLM 输出可能过长

**解决方案：**
```python
# 限制输出 token 数
MAX_OUTPUT_TOKENS = 200  # 从 500 减少到 200
MAX_SCENE_LENGTH = 150  # 场景描述最多 150 字
MAX_DIALOGUE_LENGTH = 100  # 对话回复最多 100 字
```

### 6. 使用本地模型（可选）

**如果 Ollama 可用：**
```python
# 配置 Ollama 为主要模型
PRIMARY_LLM = "ollama"  # 使用 Ollama，免费
FALLBACK_LLM = "coze"  # 仅在 Ollama 不可用时使用

# 使用更小的 Ollama 模型
OLLAMA_MODEL = "phi3:mini"  # 3B 参数，快速省 token
# OLLAMA_MODEL = "gemma2:2b"  # 2B 参数，更省 token
```

### 7. 优化 Prompt 模板

**当前（可能冗长）：**
```python
SYSTEM_PROMPT = """
你是一个专业的游戏引擎，负责生成 AI 文字冒险游戏的内容。
你的任务是根据当前的场景和玩家状态，生成引人入胜的场景描述和对话。
请确保：
1. 描述要生动形象
2. 要符合世界观设定
3. 要考虑玩家的选择和行动
4. 要保持叙事的连贯性
5. 要有适当的挑战和奖励
...
"""
```

**优化后（简洁）：**
```python
SYSTEM_PROMPT = """
AI 冒险游戏引擎。生成场景/对话，保持连贯。
世界观：末日废土，科技文明。
"""
```

**Token 节省：** ~90%

### 8. 减少重复调用

**问题：** 多次调用 LLM 生成相似内容

**解决方案：**
```python
# 批量处理
def generate_multiple_prompts(prompts):
    # ❌ 不好：逐个调用
    results = []
    for prompt in prompts:
        result = llm.generate(prompt)
        results.append(result)

    # ✅ 好：批量调用
    results = parallel_llm.generate_batch(prompts)
```

### 9. 使用更简单的输出格式

**❌ 不好的做法：**
```python
output_format = """
请以以下 JSON 格式输出：
{
    "scene_description": "...",
    "choices": ["..."],
    "npc_dialogue": "..."
}
"""
```

**✅ 好的做法：**
```python
output_format = "JSON: {scene}|{choices}|{npc}"
```

### 10. 启用上下文截断

```python
# 启用自动截断
ENABLE_CONTEXT_TRUNCATION = True
MAX_CONTEXT_TOKENS = 8000  # 从 20k 减少到 8k
CONTEXT_TRUNCATION_STRATEGY = "oldest"  # 截断最旧的消息
```

---

## 🔧 配置优化

### 1. 修改核心配置

**文件：** `core/config.py`

```python
class Settings:
    # === Token 优化 ===
    # 模型选择
    model: str = "coze/auto"
    model_small: str = "qwen-plus"  # 用于简单任务
    model_fast: str = "gemma-7b"  # 用于快速响应
    model_cheap: str = "phi-3-mini"  # 超低成本

    # Token 限制
    max_input_tokens: int = 8000  # 从 20000 减少到 8k
    max_output_tokens: int = 200  # 从 500 减少到 200
    max_context_tokens: int = 8000  # 上下文限制

    # 缓存优化
    memory_query_cache_ttl: int = 600  # 延长 TTL
    memory_query_cache_size: int = 1000  # 增加大小
    scene_description_cache_ttl: int = 1200
    scene_description_cache_size: int = 200
    embedding_cache_ttl: int = 1800
    embedding_cache_size: int = 2000

    # 上下文优化
    max_history_messages: int = 5  # 减少历史消息数量
    enable_context_truncation: bool = True  # 启用截断
    context_truncation_strategy: str = "oldest"  # 截断最旧的消息

    # 输出长度限制
    max_scene_length: int = 150
    max_dialogue_length: int = 100
    max_choice_length: int = 50
```

### 2. 修改 LLM 客户端

**文件：** `engine/llm_client.py`

```python
class LLMClient:
    def __init__(self):
        # Token 优化配置
        self.max_tokens = 200  # 减少输出 token 数
        self.temperature = 0.7  # 降低温度，减少随机性
        self.top_p = 0.9  # 使用 nucleus sampling

    def generate_text(self, prompt: str, max_tokens: int = 200):
        """生成文本（带 token 限制）"""
        # 截断过长的 prompt
        if len(prompt) > 2000:
            prompt = prompt[:2000] + "..."

        # 限制输出长度
        return self._ollama_generate(
            prompt=prompt,
            options={
                "num_predict": max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
            }
        )
```

### 3. 修改 Prompt 模板

**文件：** `engine/story_engine.py`

```python
# 简化系统提示
SYSTEM_PROMPT = """
AI 冒险游戏引擎。生成场景/对话。
世界观：末日废土，科技文明。
"""

# 简化场景生成 prompt
def create_scene_prompt(scene_id, player_state):
    return f"场景: {scene_id}|玩家: {player_state}|描述:"
```

### 4. 修改记忆管理器

**文件：** `engine/memory_manager.py`

```python
class CachedMemoryManager:
    def __init__(self):
        # 增加缓存 TTL 和大小
        self._memory_cache = TTLCache(
            default_ttl=timedelta(minutes=10),  # 从 5 分钟 → 10 分钟
            max_size=1000,  # 从 500 → 1000
            name="memory_cache"
        )

    def query_relevant(self, query: str, k: int = 3):
        """查询记忆（减少 k 值）"""
        # 减少返回结果数量
        return self._original_query(query, k=min(k, 3))
```

---

## 📊 预期效果

### Token 使用对比

| 场景 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| 场景生成 | 500 tokens | 150 tokens | **70%** |
| 对话生成 | 300 tokens | 100 tokens | **67%** |
| 记忆查询 | 200 tokens | 50 tokens | **75%** |
| 嵌入生成 | 100 tokens | 50 tokens | **50%** |
| **总体节省** | **1100 tokens** | **350 tokens** | **68%** |

### 成本对比

假设：
- 输入 token：$0.001/1k tokens
- 输出 token：$0.002/1k tokens

**优化前（每次操作）：**
- 输入：29k tokens
- 输出：11k tokens
- 成本：$0.051

**优化后（每次操作）：**
- 输入：10k tokens（缓存 84% + 优化）
- 输出：2k tokens
- 成本：$0.014

**成本降低：** **72%**

---

## 🚀 立即行动

### 1. 检查当前配置
```bash
# 查看当前模型配置
cat /workspace/projects/workspace/projects/text-adventure-game/core/config.py | grep -A 5 "class Settings"
```

### 2. 应用优化配置
根据上述建议修改配置文件

### 3. 测试效果
运行游戏，监控 token 使用情况

### 4. 监控和调整
```bash
# 使用 session_status 监控
python -c "from session_status import session_status; print(session_status())"
```

---

## 💡 额外建议

### 1. 使用更短的对话历史
- 当前：保留所有历史消息
- 建议：只保留最近 5 条消息

### 2. 压缩存储的数据
- 存档文件使用更小的格式
- 只存储必要信息

### 3. 使用本地模型
- 配置 Ollama
- 使用小型模型（phi3:mini, gemma2:2b）

### 4. 减少不必要的日志
- 关闭 DEBUG 日志
- 只记录关键信息

### 5. 使用采样而非完整输出
- 对于长文本，先返回摘要
- 用户需要时再生成完整内容

---

## 📝 总结

**关键优化点：**
1. ✅ 使用更小的模型
2. ✅ 简化 Prompt
3. ✅ 减少上下文
4. ✅ 延长缓存 TTL
5. ✅ 减少输出长度
6. ✅ 使用并行请求
7. ✅ 启用上下文截断

**预期节省：** **68% tokens**，**72% 成本**

**当前状态：**
- 缓存命中率：84% ✅
- Token 使用：40k（合理）
- 建议优化后：~13k

---

**文档时间：** 2026年4月7日 08:25
**作者：** 陳千语 🐉
