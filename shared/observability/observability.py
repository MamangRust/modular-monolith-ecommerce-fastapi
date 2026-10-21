"""Observability helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from pkg.logger.logger import Logger


class Observability:
    """Starts a structlog-bound context; OTel spans attach when telemetry
 is enabled (kept optional so unit tests run without a collector)."""

    def __init__(self, service_name: str, logger: Logger) -> None:
        self._service = service_name
        self._logger = logger

    @contextmanager
    def span(self, method: str, **attributes: Any) -> Iterator[Logger]:
        logger = self._logger.with_fields(method=method, **attributes)
        logger.debug("started", service=self._service)
        try:
            yield logger
        except Exception as exc:
            logger.error("method error", error=str(exc))
            raise
        else:
            logger.debug("method completed")
