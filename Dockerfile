# 作品集 Demo：Streamlit UI（Ollama 建議在宿主另起）
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    PYTHONIOENCODING=UTF-8

COPY requirements.txt requirements-dev.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

RUN mkdir -p data/saves data/logs data/chroma_db data/cache

EXPOSE 8501

# 如需健康檢查，可改用 compose 的 healthcheck + curl（slim 映像需自行安裝）
CMD ["python", "-m", "streamlit", "run", "frontend/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--browser.gatherUsageStats=false"]
