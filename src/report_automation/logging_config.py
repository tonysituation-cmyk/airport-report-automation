"""Logging setup: console + file, container-friendly (WatchedFileHandler
so external rotation via logrotate works in production)."""
from __future__ import annotations

import logging
from logging.handlers import WatchedFileHandler
from pathlib import Path

_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


def setup_logging(logs_dir: Path, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("report_automation")
    if logger.handlers:  # idempotent — safe for repeated runs and tests
        return logger
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = logging.Formatter(_FORMAT)

    logs_dir.mkdir(parents=True, exist_ok=True)
    file_handler = WatchedFileHandler(logs_dir / "automation.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger
