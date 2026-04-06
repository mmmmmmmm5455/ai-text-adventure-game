# 部署说明

## 本机（作品集演示）

设置 `PYTHONPATH` 为项目根目录：

```bash
export PYTHONIOENCODING=UTF-8
python -m streamlit run frontend/app.py
```

Windows 可使用 `start.bat`（内部已设置 `PYTHONPATH`、`PYTHONIOENCODING` 与 `python -m streamlit`）。

## CI

- GitHub Actions：见 `.github/workflows/ci.yml`，在 `push` / `pull_request` 时运行 `pytest`（Python 3.11、3.12）。
- 本地对齐 CI：`pip install -r requirements-dev.txt && python -m pytest tests/ -q`

## Docker（示例思路）

- 基础镜像 `python:3.11-slim`
- `pip install -r requirements.txt`
- Ollama 建议以**侧车容器**或宿主机网络访问，勿在单容器内强耦合模型拉取（体积与启动时间）
- 暴露 `8501`
- 挂载 `data/` 以持久化存档与 Chroma

生产环境请自行加固网络、HTTPS 与资源限制。

## 未来 API / 容器化

若需与前端分离：

- 将「用例层」暴露为 FastAPI/Flask，返回 JSON（`GameState` 快照或增量事件）；Streamlit 仅作演示客户端。
- 版本化剧情与存档策略见 `docs/STORY_VERSIONING.md`。
