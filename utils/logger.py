from __future__ import annotations

import logging
from datetime import datetime, tzinfo
from pathlib import Path

# Py 3.11+ fournit datetime.UTC ; sinon on retombe sur timezone.utc
try:
    from datetime import UTC  # py311+

    UTC_TZ: tzinfo = UTC
except ImportError:
    UTC_TZ = UTC

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / f"log_{datetime.now(UTC_TZ).strftime('%Y-%m-%d')}.log"

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
