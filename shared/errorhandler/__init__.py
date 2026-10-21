"""HTTP error rendering for the FastAPI gateway."""

from shared.errorhandler.errorhandler import (
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
