"""
契約測試：CI 閘道，確保敘事生成埠的方法簽名與行為底線成立。
不依賴 Ollama；可替換為 FakeLLM。
"""

from __future__ import annotations

import inspect

import pytest

from core.ports import TextGenerationPort
from engine.llm_client import LLMClient


def test_llm_client_is_structural_subtype_of_port() -> None:
    client = LLMClient()
    assert isinstance(client, TextGenerationPort)


def _annotation_is(expected: type, ann: object) -> bool:
    if ann is inspect.Signature.empty:
        return True
    if ann is expected:
        return True
    # from __future__ import annotations → 常為字串 'str' / 'bool'
    if ann == expected.__name__:
        return True
    return getattr(ann, "__name__", None) == expected.__name__


def test_generate_text_signature_stable() -> None:
    sig = inspect.signature(LLMClient.generate_text)
    names = set(sig.parameters) - {"self"}
    assert {"prompt", "system", "temperature", "max_tokens"} <= names
    assert _annotation_is(str, sig.return_annotation)


def test_health_check_signature_stable() -> None:
    sig = inspect.signature(LLMClient.health_check)
    params = [p for p in sig.parameters if p != "self"]
    assert len(params) == 0
    assert _annotation_is(bool, sig.return_annotation)


@pytest.mark.parametrize(
    "method_name",
    ("generate_text", "health_check"),
)
def test_port_methods_exist_on_llm_client(method_name: str) -> None:
    assert callable(getattr(LLMClient, method_name, None))
