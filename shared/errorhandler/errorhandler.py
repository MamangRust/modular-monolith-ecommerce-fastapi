"""Backwards-compatible shim: the envelope moved to `shared/errors/api_error.py` (matching the layout, where the HTTP rendering lives in shared/errors)."""

from shared.errors.api_error import (
    app_error_handler,
    error_payload,
    handle_error,
    http_exception_handler,
    register_exception_handlers,
    request_validation_handler,
    to_http_response,
    unhandled_exception_handler,
    validation_error_payload,
)

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
