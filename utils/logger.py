from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / f"log_{datetime.now(UTC).strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),  # aussi dans la console
    ],
)


def get_logger(name: str) -> logging.Logger:
    """Retourne un logger nommé et configuré."""
    return logging.getLogger(name)
