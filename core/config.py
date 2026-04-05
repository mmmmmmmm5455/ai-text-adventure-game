"""
应用配置：从环境变量加载路径、模型名与运行参数。
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _project_root() -> Path:
    """仓库根目录（core 的上一级）。"""
    return Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """全局配置，支持 .env 覆盖。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    ollama_base_url: str = Field(default="http://127.0.0.1:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3", alias="OLLAMA_MODEL")
    ollama_embed_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBED_MODEL")
    ollama_timeout: float = Field(default=120.0, alias="OLLAMA_TIMEOUT")
    llm_cache_enabled: bool = Field(default=True, alias="LLM_CACHE_ENABLED")
    max_user_input_length: int = Field(default=2000, alias="MAX_USER_INPUT_LENGTH")

    data_dir: Path = Field(default_factory=lambda: _project_root() / "data")
    saves_dir: Path = Field(default_factory=lambda: _project_root() / "data" / "saves")
    logs_dir: Path = Field(default_factory=lambda: _project_root() / "data" / "logs")
    chroma_dir: Path = Field(default_factory=lambda: _project_root() / "data" / "chroma_db")
    cache_dir: Path = Field(default_factory=lambda: _project_root() / "data" / "cache")

    def ensure_runtime_dirs(self) -> None:
        """创建运行时目录。"""
        for p in (self.data_dir, self.saves_dir, self.logs_dir, self.chroma_dir, self.cache_dir):
            p.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """返回单例配置。"""
    s = Settings()
    s.ensure_runtime_dirs()
    return s


def reset_settings_cache() -> None:
    """测试用：清空配置缓存。"""
    get_settings.cache_clear()
