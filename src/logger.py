"""Production-grade structured logging module.

Replaces standard print statements with a robust logging setup supporting both
console stream handlers and rotating file handlers to prevent memory overflow.
"""

import logging
from logging.handlers import RotatingFileHandler
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

    # Define standard format for structured tracking
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Stream Handler (Console Output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating File Handler (Max 50KB per file, keeping up to 3 backup files)
    file_handler = RotatingFileHandler(
        filename=LOG_FILE_PATH,
        maxBytes=50 * 1024,  # 50 KB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger


# Instantiate global module-level logger
logger = setup_logger()
