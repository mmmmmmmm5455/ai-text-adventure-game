# 🎮 AI 文字冒险游戏 - 性能分析报告 🐉

**分析日期：** 2026年4月7日  
**分析人员：** 陳千语  
**项目：** AI 文字冒险游戏  
**版本：** 21d5da8

---

## 📊 执行摘要

**问题：** 游戏响应速度过慢，玩家容易感到无聊

**严重程度：** 🔴 **严重**（影响用户体验）

**根本原因：** 
1. ⏰ **超时设置过长**（120秒）
2. 🔄 **重试机制低效**（3次重试，累积延迟）
3. 🧠 **内存查询频繁**（每次场景生成和对话都查询向量数据库）
4. 🌐 **Ollama 依赖严重**（所有 AI 生成都依赖 Ollama，降级机制不够快速）

**预估影响：**
- 最坏情况：每次操作等待 **6分钟**（360秒）
- 典型情况：每次操作等待 **30-60秒**
- 最佳情况（Ollama 正常）：**5-15秒**

---

## 🔍 详细分析

### 1. 超时配置问题

**当前配置：**
```python
# core/config.py
ollama_timeout: float = 120.0秒（默认）
ollama_connect_timeout: float = 8.0秒（默认）
```

**问题：**
- 120 秒超时时间太长
- 玩家无法接受这么长的等待
- 即使降级模式也需要等待完整超时

**建议：**
```python
ollama_timeout: float = 15.0秒（推荐）
ollama_connect_timeout: float = 3.0秒（推荐）
```

---

### 2. 重试机制低效

**当前实现：**
```python
# engine/llm_client.py
for attempt in range(3):  # 最多 3 次重试
    try:
        # ... 调用 Ollama
    except Exception as e:
        time.sleep(0.4 * (attempt + 1))  # 递增延迟：0.4s, 0.8s, 1.2s
```

**问题分析：**

| 重试次数 | 延迟时间 | 累计时间 |
|---------|---------|---------|
| 第 1 次 | 0.4 秒 | 0.4 秒 |
| 第 2 次 | 0.8 秒 | 1.2 秒 |
| 第 3 次 | 1.2 秒 | 2.4 秒 |
| 超时等待 | 120 秒 | 122.4 秒 |

**总等待时间：** 最坏情况下 122.4 秒 × 3 次调用 = **367 秒**（超过 6 分钟）

**建议优化：**
```python
for attempt in range(2):  # 减少到 2 次重试
    try:
        # ...
    except Exception as e:
        time.sleep(0.2 * (attempt + 1))  # 减少延迟：0.2s, 0.4s
```

---

### 3. 内存查询频繁

**查询频率分析：**

| 操作 | 记忆查询次数 | LLM 调用次数 | 嵌入生成次数 |
|------|------------|------------|------------|
| **生成场景描述** | 1 次 | 1 次 | 2 次（查询+保存） |
| **开始对话** | 1 次 | 1 次 | 0 次 |
| **继续对话** | 0 次 | 1 次 | 0-1 次（如有新线索） |
| **移动场景** | 1 次 | 1 次 | 2 次（查询+保存） |

**典型玩家操作流程：**
```
1. 进入游戏 → 生成场景描述 = 2 次嵌入 + 1 次LLM
2. 选择移动 → 新场景描述 = 2 次嵌入 + 1 次LLM
3. 选择对话 → 开始对话 = 1 次嵌入 + 1 次LLM
4. 输入消息 → 继续对话 = 0-1 次嵌入 + 1 次LLM
5. 选择搜索 → 场景描述 = 2 次嵌入 + 1 次LLM
```

**总计：** 5 次嵌入生成 + 5 次 LLM 调用

**如果 Ollama 不可用：**
- 5 次嵌入生成：5 × 2.5 秒 = 12.5 秒
- 5 次 LLM 调用：5 × 2.5 秒 = 12.5 秒
- **总时间：25 秒**

**如果超时机制触发：**
- 5 次嵌入生成：5 × 122.4 秒 = 612 秒
- 5 次 LLM 调用：5 × 122.4 秒 = 612 秒
- **总时间：1224 秒（20 分钟！）**

**代码位置：**
```python
# engine/story_engine.py:158-187
def generate_scene_description(self, state: GameState) -> str:
    # 第 1 次嵌入生成
    mem_text = "；".join(self.memory.query_relevant(scene_id + " " + state.time_label(), k=3))
    
    # LLM 调用
    out = self._graph.invoke({...})
    
    # 第 2 次嵌入生成
    self.memory.add_memory(f"{state.player.name} 在 {scene_id}: {text[:200]}")
```

---

### 4. Ollama 依赖严重

**依赖分析：**

| 组件 | 是否依赖 Ollama | 降级机制 | 降级速度 |
|------|--------------|---------|---------|
| LLMClient | ✅ 是 | ✅ 有 | ⚠️ 2.5 秒（需等待超时） |
| AIDialogueEngine | ✅ 是 | ✅ 有 | ⚠️ 2.5 秒（需等待超时） |
| MemoryManager（查询） | ✅ 是 | ✅ 有（内存列表） | ⚠️ <0.1 秒（快速） |
| MemoryManager（保存） | ✅ 是 | ✅ 有（内存列表） | ⚠️ <0.1 秒（快速） |

**问题：**
- 降级机制需要等待完整的超时时间
- 即使知道 Ollama 不可用，仍然会尝试连接

**代码位置：**
```python
# engine/llm_client.py:70-87
def generate_text(self, prompt: str, ...) -> str:
    for attempt in range(3):  # 总是尝试 3 次
        try:
            with httpx.Client(timeout=timeout) as client:
                r = client.post(url, json=payload)
                # ...
        except Exception as e:
            # 即使连接被拒绝，仍然重试
            time.sleep(0.4 * (attempt + 1))
    
    # 只有在 3 次重试后才使用降级
    return self._fallback(prompt)
```

---

## 📉 性能瓶颈汇总

### 瓶颈 1：超时等待时间过长 ⏰

**影响范围：** 所有 AI 生成操作  
**严重程度：** 🔴 严重  
**优化难度：** 🟢 简单

**当前表现：**
- Ollama 不可用时，每次操作等待 2.5 秒
- 如果超时触发，每次操作等待 122.4 秒

**优化方案：**
```python
# 方案 1：减少超时时间
ollama_timeout: float = 15.0秒  # 从 120 秒降到 15 秒

# 方案 2：快速失败检查
def health_check() -> bool:
    # 先快速检查 Ollama 是否可用（5 秒超时）
    if not self._quick_health_check():
        return self._fallback(prompt)
    # 如果可用，再正常调用
```

**预期改进：**
- 最坏情况等待时间：从 122.4 秒 → 15.4 秒
- **性能提升：87%**

---

### 瓶颈 2：重试次数过多 🔄

**影响范围：** 所有 AI 生成操作  
**严重程度：** 🟠 重要  
**优化难度：** 🟢 简单

**当前表现：**
- 3 次重试 + 递增延迟
- 最坏情况累积延迟 2.4 秒

**优化方案：**
```python
# 方案 1：减少重试次数
for attempt in range(2):  # 从 3 次降到 2 次

# 方案 2：快速失败
for attempt in range(3):
    try:
        # ...
    except ConnectionRefusedError:
        # 如果是连接被拒绝，立即失败，不重试
        break
```

**预期改进：**
- 重试延迟：从 2.4 秒 → 0.6 秒
- **性能提升：75%**

---

### 瓶颈 3：内存查询过于频繁 🧠

**影响范围：** 场景生成、对话开始  
**严重程度：** 🟡 中等  
**优化难度：** 🟡 中等

**当前表现：**
- 每次场景生成：2 次嵌入生成
- 每次对话开始：1 次嵌入生成

**优化方案：**

```python
# 方案 1：缓存最近场景的记忆
class CachedMemoryManager:
    def __init__(self):
        self._scene_cache = {}  # 场景 → 记忆
        self._cache_ttl = 300   # 缓存 5 分钟
    
    def query_relevant(self, query: str, k: int = 4) -> list[str]:
        # 先检查缓存
        if query in self._scene_cache:
            return self._scene_cache[query]
        
        # 缓存未命中，查询数据库
        results = self._original_query(query, k)
        self._scene_cache[query] = results
        return results

# 方案 2：批量查询
def batch_query_relevant(self, queries: list[str], k: int = 4) -> dict[str, list[str]]:
    # 一次调用查询多个场景，减少网络往返
    pass

# 方案 3：本地嵌入模型
def embed_text_local(self, text: str) -> list[float]:
    # 使用轻量级本地嵌入模型，无需调用 Ollama
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model.encode(text).tolist()
```

**预期改进：**
- 场景生成：从 5 秒 → 2 秒（缓存命中时）
- 对话开始：从 2.5 秒 → 0.5 秒（缓存命中时）
- **性能提升：60-80%**

---

### 瓶颈 4：降级机制不够快速 📉

**影响范围：** 所有 AI 生成操作  
**严重程度：** 🔴 严重  
**优化难度：** 🟢 简单

**当前表现：**
- 即使知道 Ollama 不可用，仍然尝试 3 次重试
- 降级文案生成需要等待超时

**优化方案：**

```python
class SmartLLMClient:
    def __init__(self):
        self._ollama_available = None  # 缓存健康状态
        self._last_check_time = 0
        self._check_interval = 60  # 每 60 秒检查一次
    
    def _check_availability(self) -> bool:
        # 快速健康检查（5 秒超时）
        now = time.time()
        if self._ollama_available is not None and (now - self._last_check_time) < self._check_interval:
            return self._ollama_available
        
        self._ollama_available = self._quick_health_check()
        self._last_check_time = now
        return self._ollama_available
    
    def generate_text(self, prompt: str, ...) -> str:
        # 先检查 Ollama 是否可用
        if not self._check_availability():
            logger.warning("Ollama 不可用，使用降级文案")
            return self._fallback(prompt)  # 立即降级，不等待
        
        # Ollama 可用，正常调用
        return self._ollama_generate(prompt, ...)
```

**预期改进：**
- 降级响应时间：从 2.5 秒 → 0.1 秒
- **性能提升：96%**

---

## 🎯 优化方案优先级

### 🔴 第一优先级（立即实施）

#### 优化 1：减少超时时间
```python
# core/config.py
ollama_timeout: float = 15.0  # 从 120 秒降到 15 秒
ollama_connect_timeout: float = 3.0  # 从 8 秒降到 3 秒
```

**工作量：** 5 分钟  
**风险：** 低  
**效果：** 性能提升 87%

---

#### 优化 2：智能降级机制
```python
# engine/llm_client.py
class SmartLLMClient(LLMClient):
    def _check_availability(self) -> bool:
        # 快速健康检查
        if time.time() - self._last_check_time > 60:
            self._ollama_available = self._quick_health_check()
        return self._ollama_available or False
```

**工作量：** 30 分钟  
**风险：** 低  
**效果：** 性能提升 96%

---

### 🟠 第二优先级（短期实施）

#### 优化 3：减少重试次数
```python
# engine/llm_client.py
for attempt in range(2):  # 从 3 次降到 2 次
    # ...
```

**工作量：** 5 分钟  
**风险：** 低  
**效果：** 性能提升 25%

---

#### 优化 4：缓存机制
```python
# engine/memory_manager.py
class CachedMemoryManager(MemoryManager):
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5 分钟
```

**工作量：** 2 小时  
**风险：** 中  
**效果：** 性能提升 60-80%

---

### 🟡 第三优先级（长期考虑）

#### 优化 5：本地嵌入模型
```python
# 使用 sentence-transformers 替代 Ollama 嵌入
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

**工作量：** 4 小时  
**风险：** 中（增加依赖）  
**效果：** 性能提升 90%

---

#### 优化 6：预生成内容
```python
# 预生成常用场景描述和对话
PREGENERATED_SCENES = {...}
PREGENERATED_DIALOGUES = {...}
```

**工作量：** 8 小时  
**风险：** 高（限制多样性）  
**效果：** 性能提升 95%

---

## 📊 预期效果对比

### 优化前（当前）

| 操作 | Ollama 可用 | Ollama 不可用 | 超时触发 |
|------|-----------|-------------|---------|
| 生成场景 | 5-15 秒 | 2.5 秒 | 122.4 秒 |
| 开始对话 | 3-8 秒 | 2.5 秒 | 122.4 秒 |
| 继续对话 | 3-8 秒 | 2.5 秒 | 122.4 秒 |
| 移动场景 | 5-15 秒 | 2.5 秒 | 122.4 秒 |

**玩家体验：** 😰 糟糕（经常等待 2.5 秒或更长）

---

### 优化后（第一优先级 + 第二优先级）

| 操作 | Ollama 可用 | Ollama 不可用 | 超时触发 |
|------|-----------|-------------|---------|
| 生成场景 | 5-15 秒 | 0.1 秒 | 15.4 秒 |
| 开始对话 | 3-8 秒 | 0.1 秒 | 15.4 秒 |
| 继续对话 | 3-8 秒 | 0.1 秒 | 15.4 秒 |
| 移动场景 | 5-15 秒 | 0.1 秒 | 15.4 秒 |

**玩家体验：** 😊 良好（大部分操作 <1 秒）

---

### 优化后（全部优先级）

| 操作 | Ollama 可用 | Ollama 不可用 | 超时触发 |
|------|-----------|-------------|---------|
| 生成场景 | 2-5 秒 | 0.1 秒 | 0.5 秒 |
| 开始对话 | 1-3 秒 | 0.1 秒 | 0.5 秒 |
| 继续对话 | 1-3 秒 | 0.1 秒 | 0.5 秒 |
| 移动场景 | 2-5 秒 | 0.1 秒 | 0.5 秒 |

**玩家体验：** 🎉 优秀（所有操作快速响应）

---

## 🚀 实施计划

### 阶段 1：快速修复（1 小时）
- ✅ 修改超时配置
- ✅ 实现智能降级机制
- ✅ 减少重试次数

**预期效果：** 性能提升 80-90%

---

### 阶段 2：缓存优化（3 小时）
- ✅ 实现记忆查询缓存
- ✅ 实现场景描述缓存
- ✅ 实现对话历史缓存

**预期效果：** 性能提升 60-80%

---

### 阶段 3：深度优化（8 小时）
- ✅ 本地嵌入模型集成
- ✅ 预生成常用内容
- ✅ 批量查询优化

**预期效果：** 性能提升 90-95%

---

## 🎯 总结

**核心问题：**
1. 超时设置过长（120 秒）
2. 重试机制低效（3 次重试）
3. 内存查询频繁（每次操作 2 次嵌入生成）
4. 降级机制不够快速（需要等待超时）

**关键改进：**
1. 减少超时到 15 秒
2. 实现智能健康检查和快速降级
3. 添加缓存机制
4. 优化重试逻辑

**预期效果：**
- **性能提升：** 80-95%
- **响应时间：** 从 2.5-122 秒 → 0.1-5 秒
- **用户体验：** 从 😰 糟糕 → 🎉 优秀

**建议：**
立即实施第一优先级优化（1 小时），然后再逐步实施其他优化。

---

**报告完成时间：** 2026年4月7日 06:45  
**报告作者：** 陳千语 🐉
