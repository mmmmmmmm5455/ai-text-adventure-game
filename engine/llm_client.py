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
    性能优化：智能降级 + 快速失败
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._cache: dict[str, str] = {}
        # 性能优化：缓存健康状态，避免每次都检查
        self._ollama_available: bool | None = None
        self._last_check_time: float = 0
        self._check_interval: float = 60  # 每 60 秒检查一次

    def _cache_key(self, prompt: str, model: str) -> str:
        raw = f"{model}::{prompt}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def _check_availability(self) -> bool:
        """性能优化：快速检查 Ollama 是否可用（带缓存）"""
        now = time.time()

        # 缓存健康状态，避免频繁检查
        if self._ollama_available is not None and (now - self._last_check_time) < self._check_interval:
            return self._ollama_available

        # 缓存未命中或已过期，执行健康检查
        self._ollama_available = self._quick_health_check()
        self._last_check_time = now

        return self._ollama_available or False

    def _quick_health_check(self) -> bool:
        """性能优化：快速健康检查（5 秒超时）"""
        url = f"{self._settings.ollama_base_url.rstrip('/')}/api/tags"
        try:
            with httpx.Client(timeout=5.0) as client:
                r = client.get(url)
                r.raise_for_status()
                return True
        except Exception as e:
            logger.warning("Ollama 快速健康检查失败：{}", e)
            return False

    def generate_text(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        """生成文本；失败时返回降级文案。

        性能优化：
        1. 智能降级：先检查 Ollama 是否可用，不可用则立即降级
        2. 减少重试：从 3 次减少到 2 次
        3. 快速失败：连接被拒绝时立即失败，不重试
        4. 减少延迟：重试延迟从 0.4s 减少到 0.2s
        """
        model = self._settings.ollama_model
        sys_merged = merged_system_prompt(system)

        # 检查缓存
        if self._settings.llm_cache_enabled:
            key = self._cache_key(prompt + (sys_merged or ""), model)
            if key in self._cache:
                return self._cache[key]

        # 性能优化：智能降级 - 先检查 Ollama 是否可用
        if not self._check_availability():
            logger.warning("Ollama 不可用，使用降级文案（智能降级）")
            return self._fallback(prompt)

        # Ollama 可用，正常调用
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
        timeout = httpx.Timeout(
            self._settings.ollama_timeout,
            connect=min(self._settings.ollama_connect_timeout, self._settings.ollama_timeout),
        )

        # 性能优化：减少重试次数从 3 次到 2 次
        for attempt in range(2):
            try:
                with httpx.Client(timeout=timeout) as client:
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
            except ConnectionRefusedError as e:
                # 性能优化：快速失败 - 连接被拒绝时立即失败，不重试
                logger.warning("Ollama 连接被拒绝，立即失败（快速失败）")
                last_err = e
                break
            except Exception as e:
                last_err = e
                # 性能优化：减少重试延迟从 0.4s 到 0.2s
                logger.warning("Ollama 调用失败（第 {} 次）：{}", attempt + 1, e)
                time.sleep(0.2 * (attempt + 1))

        # 使用降级文案
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
    timeout = httpx.Timeout(
        settings.ollama_timeout,
        connect=min(settings.ollama_connect_timeout, settings.ollama_timeout),
    )
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            emb = data.get("embedding")
            if isinstance(emb, list):
                return [float(x) for x in emb]
    except Exception as e:
        logger.warning("嵌入生成失败：{}", e)
    return []
