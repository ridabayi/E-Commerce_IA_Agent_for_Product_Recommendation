from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)  # PTH103 ok

LOG_FILE = LOGS_DIR / f"log_{datetime.now(UTC).strftime('%Y-%m-%d')}.log"  # PTH118 + DTZ005 ok

logging.basicConfig(
    filename=str(LOG_FILE),
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    level=logging.INFO,
)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
