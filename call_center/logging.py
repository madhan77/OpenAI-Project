"""Logging helpers configured for structured observability."""
from __future__ import annotations

import logging
from typing import Optional

import structlog


def configure_logging(*, level: int = logging.INFO) -> None:
    """Configure structlog with JSON output suitable for production."""

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=level)


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    return structlog.get_logger(name)


__all__ = ["configure_logging", "get_logger"]

