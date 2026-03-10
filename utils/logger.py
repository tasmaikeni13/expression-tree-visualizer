"""
Logger — simple logging helper.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides a configured logger that writes to both console and
an optional file, used for debugging and export of explanation logs.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional

_LOGGER_NAME = "expression_tree_visualizer"


def get_logger(log_file: Optional[str] = None) -> logging.Logger:
    """Return the application logger, creating it on first call.

    Parameters:
        log_file: Optional path to also write log entries to a file.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("[%(asctime)s] %(levelname)s  %(message)s",
                            datefmt="%H:%M:%S")

    # Console handler
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # File handler (optional)
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
