"""
應用核心對外依賴的抽象邊界（Ports / Protocol）。

作品集專案採漸進式 DIP：新程式碼優先依賴此處 Protocol，
既有 `LLMClient` 以結構化子型別滿足契約，無需一次性重構全庫。
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class TextGenerationPort(Protocol):
    """敘事用文字生成：實作須可在 CI 中替換為假物件，且不依賴 Ollama。"""

    def generate_text(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str: ...

    def health_check(self) -> bool: ...
