# 开发说明

## 运行测试

```bash
python -m pytest tests -q
```

## 日志

日志目录：`data/logs/app.log`（运行时自动创建）。

## 依赖

核心见 `requirements.txt`；开发见 `requirements-dev.txt`。

## 架构要点

- 引擎与内容分离：`engine/` 不硬编码具体剧情数值。  
- LLM 失败路径：`engine/llm_client.py` 与对话引擎均有降级。  
