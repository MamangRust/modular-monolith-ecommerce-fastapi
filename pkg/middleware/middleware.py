"""gRPC handler middleware.

`grpc_method` wraps an async grpc.aio servicer method so that:

- every call gets a request id (contextvar) for log correlation,
- an unexpected exception is logged and returned as a gRPC INTERNAL,
- an `AppError` is returned with its original HTTP code preserved in the
 `pb.common.ErrorResponse` status detail (see shared.errors.grpc).

grpc.aio only accepts a proper status through `context.abort`, so the
wrapper aborts with the mapped status instead of re-raising."""

from __future__ import annotations

import contextvars
import functools
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from pkg.logger.logger import Logger, get_logger
from shared.errors.core import as_app_error
from shared.errors.grpc import abort_with_error

_request_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


def generate_request_id() -> str:
    return uuid.uuid4().hex


def with_request_id(request_id: str | None = None) -> str:
    value = request_id or generate_request_id()
    _request_id.set(value)
    return value


def request_id() -> str:
    return _request_id.get() or ""


def deadline_context(seconds: float) -> tuple[float, Callable[[], float]]:
    start = time.monotonic()
    return start, lambda: max(0.0, seconds - (time.monotonic() - start))


def _logger_for(servicer: Any, service: str) -> Logger:
    logger = getattr(servicer, "logger", None)
    if isinstance(logger, Logger):
        return logger
    return get_logger(service or "grpc")


def grpc_method(method: str, service: str = "") -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Decorate a grpc.aio servicer method with request-id + error mapping."""

    def decorator(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(fn)
        async def wrapper(self: Any, request: Any, context: Any) -> Any:
            rid = with_request_id()
            logger = _logger_for(self, service)
            logger.debug("grpc method started", method=method, request_id=rid)
            try:
                return await fn(self, request, context)
            except Exception as exc:
                app_error = as_app_error(exc)
                logger.error(
                    "grpc method failed",
                    method=method,
                    request_id=rid,
                    error=app_error.message,
                    error_type=app_error.type,
                    code=app_error.code,
                    cause=str(exc.__cause__ or exc),
                )
                await abort_with_error(context, app_error)

        return wrapper

    return decorator


__all__ = [
    "deadline_context",
    "generate_request_id",
    "grpc_method",
    "request_id",
    "with_request_id",
]
