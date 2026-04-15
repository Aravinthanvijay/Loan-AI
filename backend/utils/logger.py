"""
Structured logging setup with file rotation.
"""

import logging
import logging.handlers
import os
from backend.config import settings


def setup_logger(name: str = "loan_underwriting") -> logging.Logger:
    """Setup structured logger with console and file handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler (UTF-8 encoding to support emoji on Windows)
    import sys
    console_handler = logging.StreamHandler(stream=open(
        sys.stdout.fileno(), mode='w', encoding='utf-8', errors='replace', closefd=False
    ))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger