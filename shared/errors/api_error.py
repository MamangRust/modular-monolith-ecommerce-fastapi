"""HTTP rendering of AppError. `HandleApiError` clamps an out-of-range code to 500 so a bad factory call cannot emit a nonsense HTTP status, and the response shape keeps the fields (`status`, `message`, `type`, `code`, `trace_id`, `retryable`, `validations`). This module is the canonical home of the envelope; `shared/errorhandler/` re-exports it for backwards compatibility."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from shared.errors.core import (
    AppError,
    ErrorType,
    ValidationError,
    as_app_error,
    is_valid_http_code,
)


def _trace_id(request: Request | None) -> str:
    if request is None:
        return ""
    state = getattr(request, "state", None)
    if state is not None:
        value = getattr(state, "request_id", None)
        if value:
            return str(value)
    return request.headers.get("X-Request-ID", "")


def error_payload(err: AppError, request: Request | None = None) -> dict[str, Any]:
    code = err.code if is_valid_http_code(err.code) else 500
    payload: dict[str, Any] = {
        "status": "error",
        "message": err.message,
        "type": err.type,
        "code": code,
    }
    trace_id = _trace_id(request)
    if trace_id:
        payload["trace_id"] = trace_id
    if err.retryable:
        payload["retryable"] = True
    if err.validations:
        payload["validations"] = [
            {"field": v.field, "message": v.message} for v in err.validations
        ]
    return payload


def to_http_response(err: AppError, request: Request | None = None) -> JSONResponse:
    code = err.code if is_valid_http_code(err.code) else 500
    return JSONResponse(status_code=code, content=error_payload(err, request))


def validation_error_payload(exc: RequestValidationError) -> AppError:
    validations = [
        ValidationError(
            field=".".join(str(part) for part in error.get("loc", ()) if part != "body"),
            message=error.get("msg", "invalid value"),
        )
        for error in exc.errors()
    ]
    return AppError(
        type=ErrorType.BAD_REQUEST.value,
        code=400,
        message="Validation failed",
        validations=tuple(validations),
    )


async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return to_http_response(as_app_error(exc), request)


async def request_validation_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    if isinstance(exc, RequestValidationError):
        return to_http_response(validation_error_payload(exc), request)
    return to_http_response(as_app_error(exc), request)


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": str(exc.detail), "code": exc.status_code},
        )
    return to_http_response(as_app_error(exc), request)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return to_http_response(as_app_error(exc), request)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


def handle_error(err: BaseException, operation: str = "", logger: Any = None) -> AppError:
    """Normalise + log an error, errorhandler.HandleError. The returned AppError is what the caller propagates; logging stays here so every layer reports failures the same way."""
    app_error = as_app_error(err)
    if logger is not None:
        logger.error(
            operation or "request failed",
            error=app_error.message,
            error_type=app_error.type,
            code=app_error.code,
            cause=str(app_error.internal) if app_error.internal is not None else "",
        )
    return app_error


__all__ = [
    "app_error_handler",
    "error_payload",
    "handle_error",
    "http_exception_handler",
    "register_exception_handlers",
    "request_validation_handler",
    "to_http_response",
    "unhandled_exception_handler",
    "validation_error_payload",
]
