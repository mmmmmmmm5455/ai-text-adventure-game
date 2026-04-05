"""
日志初始化：loguru 输出到控制台与 data/logs。
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from core.config import get_settings


def setup_logging() -> None:
    """配置 loguru：控制台 + 滚动文件。"""
    settings = get_settings()
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    log_path: Path = settings.logs_dir / "app.log"

    logger.remove()
    logger.add(sys.stderr, level="INFO", enqueue=True)
    logger.add(
        str(log_path),
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
        level="DEBUG",
        enqueue=True,
    )
