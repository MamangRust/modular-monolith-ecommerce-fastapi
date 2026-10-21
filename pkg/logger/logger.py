"""Structured logging. keeps the same surface: a named logger per service, debug/info/warning/error levels, structured fields, and an optional OTel trace-span correlation."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "error": logging.ERROR,
}


class Logger:
    """Thin wrapper the LoggerInterface."""

    def __init__(self, service: str, level: str = "info") -> None:
        self.service = service
        self._level = _LEVELS.get(level, logging.INFO)
        self._log = structlog.get_logger(service)

    def _write(self, level: int, message: str, **fields: Any) -> None:
        if level < self._level:
            return
        if level == logging.DEBUG:
            self._log.debug(message, **fields)
        elif level == logging.WARNING:
            self._log.warning(message, **fields)
        elif level == logging.ERROR:
            self._log.error(message, **fields)
        else:
            self._log.info(message, **fields)

    def debug(self, message: str, **fields: Any) -> None:
        self._write(logging.DEBUG, message, **fields)

    def info(self, message: str, **fields: Any) -> None:
        self._write(logging.INFO, message, **fields)

    def warn(self, message: str, **fields: Any) -> None:
        self._write(logging.WARNING, message, **fields)

    def error(self, message: str, **fields: Any) -> None:
        self._write(logging.ERROR, message, **fields)

    def with_fields(self, **fields: Any) -> Logger:
        clone = Logger(self.service, logging.getLevelName(self._level).lower())
        clone._log = self._log.bind(**fields)
        return clone

    def sync(self) -> None:
        """No-op for LoggerInterface."""


def configure_stdlib() -> None:
    """Route structlog -> stdlib -> stdout once at process start."""
    logging.basicConfig(
        stream=sys.stdout,
        format="%(message)s",
        level=logging.INFO,
        force=True,
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.KeyValueRenderer(
                key_order=["event", "service", "trace_id"]
            ),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


_loggers: dict[str, Logger] = {}


def get_logger(service: str, level: str = "info") -> Logger:
    configure_stdlib()
    logger = _loggers.get(service)
    if logger is None or logger._level != _LEVELS.get(level, logging.INFO):
        logger = Logger(service, level)
        _loggers[service] = logger
    return logger
