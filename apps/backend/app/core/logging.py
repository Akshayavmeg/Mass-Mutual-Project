"""Logging foundation.

Per docs/36_Development_Guidelines.md Section 23, application logs must
never contain complete account numbers, personal information, authentication
credentials, API keys, or sensitive cheque images. This module only sets up
the logging format/handlers; callers remain responsible for not passing
sensitive values into log messages.
"""

from __future__ import annotations

import logging
import sys

from app.core.config import settings

_LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s - %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def configure_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if configure_logging() is called more than once
    # (e.g. once by the app, once by a test importing the same module).
    if root_logger.handlers:
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
