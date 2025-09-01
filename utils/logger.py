from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# OK pour Python 3.10+ : timezone.utc
LOG_FILE = LOGS_DIR / f"log_{datetime.now(UTC).strftime('%Y-%m-%d')}.log"

# Handlers
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
console_handler = logging.StreamHandler()

fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
file_handler.setFormatter(fmt)
console_handler.setFormatter(fmt)

root = logging.getLogger()
root.handlers.clear()
root.setLevel(logging.INFO)
root.addHandler(file_handler)
root.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
