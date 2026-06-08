"""
Logging utility module.
Configures a rotating file + console logger for the entire agent application.
"""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler

_LOG_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "logs", "agent.log")
)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named, configured logger instance.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        Configured Logger instance with file and console handlers.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level = getattr(
        logging,
        os.getenv("LOG_LEVEL", "INFO").upper(),
        logging.INFO,
    )
    logger.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    os.makedirs(os.path.dirname(_LOG_FILE), exist_ok=True)
    fh = RotatingFileHandler(
        _LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    fh.setFormatter(fmt)
    fh.setLevel(level)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(logging.DEBUG)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
