"""
Ollama HTTP 封装：重试、超时、可选缓存、失败时降级文案。
"""

from __future__ import annotations

import hashlib
import time
from typing import Any

import httpx
from loguru import logger

from core.config import get_settings
from core.narrative_language import merged_system_prompt, offline_llm_fallback


class LLMClient:
    """通过 Ollama REST API 调用本地模型。

    結構上滿足 ``core.ports.TextGenerationPort``，供契約測試與依賴注入演進。
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._cache: dict[str, str] = {}

    def _cache_key(self, prompt: str, model: str) -> str:
        raw = f"{model}::{prompt}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def generate_text(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        """生成文本；失败时返回降级文案。"""
        model = self._settings.ollama_model
        sys_merged = merged_system_prompt(system)
        if self._settings.llm_cache_enabled:
            key = self._cache_key(prompt + (sys_merged or ""), model)
            if key in self._cache:
                return self._cache[key]

        url = f"{self._settings.ollama_base_url.rstrip('/')}/api/chat"
        messages: list[dict[str, str]] = []
        if sys_merged:
            messages.append({"role": "system", "content": sys_merged})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        last_err: Exception | None = None
        for attempt in range(3):
            try:
                with httpx.Client(timeout=self._settings.ollama_timeout) as client:
                    r = client.post(url, json=payload)
                    r.raise_for_status()
                    data = r.json()
                    text = (
                        data.get("message", {}).get("content")
                        or data.get("response")
                        or ""
                    ).strip()
                    if not text:
                        raise ValueError("空响应")
                    if self._settings.llm_cache_enabled:
                        self._cache[self._cache_key(prompt + (sys_merged or ""), model)] = text
                    return text
            except Exception as e:
                last_err = e
                logger.warning("Ollama 调用失败（第 {} 次）：{}", attempt + 1, e)
                time.sleep(0.4 * (attempt + 1))

        err_s = str(last_err)
        logger.error("Ollama 不可用，使用降级文案。原因：{}", last_err)
        if "404" in err_s:
            logger.error(
                "出现 404 时常见原因：① 11434 端口不是 Ollama（被其它程序占用）；"
                "② 未安装/未启动 Ollama；③ 需在终端执行：ollama pull {}",
                model,
            )
        return self._fallback(prompt)

    def _fallback(self, prompt: str) -> str:
        """离线降级：简短叙事占位，保证界面可演示。"""
        return offline_llm_fallback()

    def health_check(self) -> bool:
        """检测 Ollama 是否可用。"""
        url = f"{self._settings.ollama_base_url.rstrip('/')}/api/tags"
        try:
            with httpx.Client(timeout=5.0) as client:
                r = client.get(url)
                r.raise_for_status()
                data = r.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                logger.info("Ollama 可用，已发现模型：{}", models)
                return True
        except Exception as e:
            logger.warning("Ollama 健康检查失败：{}", e)
            return False


def ollama_embed_text(text: str, model: str | None = None) -> list[float]:
    """
    使用 Ollama 嵌入 API 生成向量（供 Chroma 使用）。
    若失败返回空列表，由上层决定是否降级。
    """
    settings = get_settings()
    m = model or settings.ollama_embed_model
    url = f"{settings.ollama_base_url.rstrip('/')}/api/embeddings"
    payload = {"model": m, "prompt": text}
    try:
        with httpx.Client(timeout=settings.ollama_timeout) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            emb = data.get("embedding")
            if isinstance(emb, list):
                return [float(x) for x in emb]
    except Exception as e:
        logger.warning("嵌入生成失败：{}", e)
    return []
