"""记忆检索：嵌入失败时走降级路径，关键词应能召回。"""

from __future__ import annotations

from unittest.mock import patch

from engine.memory_manager import MemoryManager


@patch("engine.memory_manager.ollama_embed_text", return_value=[])
def test_memory_fallback_keyword_retrieval(_mock_emb: object) -> None:
    mm = MemoryManager()
    token = "ZyzzyvaMarkerQuest8142"
    mm.add_memory(f"你在井边听见低语，提到{token}与旧塔。", {"test": True})
    hits = mm.query_relevant(token, k=4)
    assert hits
    assert any(token in h for h in hits)
