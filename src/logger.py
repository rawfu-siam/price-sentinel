"""Production-grade structured logging module.

Replaces standard print statements with a robust logging setup supporting both
console stream handlers and rotating file handlers to prevent memory overflow.
"""

import logging
from pathlib import Path

from src.config import settings

# Define logs directory relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE_PATH = LOG_DIR / "app.log"


def setup_logger(name: str = "price_sentinel") -> logging.Logger:
    """Configure and return a production-grade logger with rotation."""
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    # Set base logging level from validated settings
    numeric_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
