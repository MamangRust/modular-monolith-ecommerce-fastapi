"""Typed application errors. `AppError` is the single error type crossing layer boundaries. It carries an HTTP code that the gateway renders directly and that the gRPC layer converts to a `google.rpc.Status` code, so a 404 in a repository surfaces as a 404 in REST instead of being flattened to 500."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, dataclass, field, replace
from enum import StrEnum

from pkg.database.errors import NoRowsError, is_foreign_key_violation, is_unique_violation

# CPython and `contextlib` attach these to an exception while it propagates
# (notably `exc.__traceback__ = tb` in a generator-based `with` block). A
# frozen dataclass rejects every assignment, so without this exemption an
# AppError raised inside `with obs.span(...)` would be replaced by a
# FrozenInstanceError and surface as a 500 instead of its real code.
_EXCEPTION_BOOKKEEPING = frozenset(
    {
        "__traceback__",
        "__cause__",
        "__context__",
        "__suppress_context__",
        "__notes__",
    }
)


class ErrorType(StrEnum):
    INTERNAL = "INTERNAL"
    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"
    CONFLICT = "CONFLICT"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    TIMEOUT = "TIMEOUT"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class ValidationError:
    field: str
    message: str


@dataclass(frozen=True)
class AppError(Exception):
    """`type` is a plain string because gRPC status details may carry the HTTP reason phrase (see `new_grpc_error`), matching the `ErrorType`."""

    type: str = ErrorType.INTERNAL.value
    code: int = 500
    message: str = "Internal server error"
    retryable: bool = False
    validations: tuple[ValidationError, ...] = ()
    internal: BaseException | None = field(default=None, compare=False, repr=False)

    def __str__(self) -> str:
        return self.message

    def with_internal(self, internal: BaseException | None) -> AppError:
        return replace(self, internal=internal)

    def with_message(self, message: str) -> AppError:
        return replace(self, message=message)

    def with_validations(self, validations: list[ValidationError]) -> AppError:
        return replace(self, validations=tuple(validations))

    def as_retryable(self) -> AppError:
        return replace(self, retryable=True)

    def is_(self, target: AppError) -> bool:
        """Approximate `errors.Is` for AppError sentinels."""
        return (
            self.type == target.type
            and self.code == target.code
            and self.message == target.message
        )


def _app_error_setattr(self: AppError, name: str, value: object) -> None:
    """Frozen for data fields, writable for Python's exception bookkeeping. `contextlib`'s generator-based `with` re-raises via `exc.__traceback__ = tb`, so a strictly frozen exception turns any error raised inside a `with` block into a FrozenInstanceError (observed as a 500 instead of 404/409). Assigning `__setattr__` after `@dataclass(frozen=True)` is the only way to keep both properties: the decorator refuses to let a class body define it."""
    if name in _EXCEPTION_BOOKKEEPING:
        object.__setattr__(self, name, value)
        return
    raise FrozenInstanceError(f"cannot assign to field {name!r}")


AppError.__setattr__ = _app_error_setattr  # type: ignore[assignment]


def is_valid_http_code(code: int) -> bool:
    return 100 <= code <= 599


# sentinels (shared/errors/core.var block) ----

err_bad_request = AppError(ErrorType.BAD_REQUEST.value, 400, "Bad request")
err_validation_failed = AppError(ErrorType.BAD_REQUEST.value, 400, "Validation failed")
err_unauthorized = AppError(ErrorType.UNAUTHORIZED.value, 401, "Unauthorized")
err_forbidden = AppError(ErrorType.FORBIDDEN.value, 403, "Forbidden")
err_not_found = AppError(ErrorType.NOT_FOUND.value, 404, "Resource not found")
err_conflict = AppError(ErrorType.CONFLICT.value, 409, "Resource conflict")
err_too_many_requests = AppError(
    ErrorType.BAD_REQUEST.value, 429, "Too many requests", retryable=True
)
err_internal = AppError(ErrorType.INTERNAL.value, 500, "Internal server error")
err_service_unavailable = AppError(
    ErrorType.UNAVAILABLE.value, 503, "Service unavailable", retryable=True
)
err_timeout = AppError(ErrorType.TIMEOUT.value, 504, "Request timeout", retryable=True)

# Domain sentinels.
err_user_not_found = AppError(ErrorType.NOT_FOUND.value, 404, "user not found")
err_role_not_found = AppError(ErrorType.NOT_FOUND.value, 404, "role not found")
err_token_not_found = AppError(ErrorType.NOT_FOUND.value, 404, "token not found")
err_find_by_user_id = AppError(ErrorType.INTERNAL.value, 500, "Failed to find by user id")
err_parse_date = AppError(ErrorType.BAD_REQUEST.value, 400, "Failed to parse date")


# ---- factories ----

def err_failed(operation: str) -> AppError:
    return err_internal.with_message(f"Failed to {operation}")


def err_not_found_response(entity: str) -> AppError:
    return err_not_found.with_message(f"{entity} not found")


def err_no_rows_or_failed(err: BaseException, entity: str, operation: str) -> AppError:
    if isinstance(err, NoRowsError):
        return err_not_found_response(entity).with_internal(err)
    return err_failed(operation).with_internal(err)


def err_constraint_or_failed(err: BaseException, entity: str, operation: str) -> AppError:
    if is_unique_violation(err):
        return err_conflict.with_message(f"{entity} already exists").with_internal(err)
    if is_foreign_key_violation(err):
        return err_bad_request.with_message(
            f"invalid related {entity} reference"
        ).with_internal(err)
    return err_no_rows_or_failed(err, entity, operation)


def new_bad_request_error(message: str) -> AppError:
    return err_bad_request.with_message(message)


def new_not_found_error(resource: str) -> AppError:
    return err_not_found.with_message(f"{resource} not found")


def new_conflict_error(message: str) -> AppError:
    return err_conflict.with_message(message)


def new_internal_error(err: BaseException | None = None) -> AppError:
    return err_internal.with_internal(err)


def new_service_unavailable_error(service: str) -> AppError:
    return err_service_unavailable.with_message(f"{service} is temporarily unavailable")


def new_forbidden_error(message: str) -> AppError:
    return err_forbidden.with_message(message)


def new_unauthorized_error(message: str) -> AppError:
    return err_unauthorized.with_message(message)


def new_validation_error(validations: list[ValidationError]) -> AppError:
    return err_validation_failed.with_validations(validations)


def new_error_response(message: str, code: int) -> AppError:
    """NewErrorResponse: leaves Type at its zero value, so the wire detail carries an empty type."""
    return AppError(type="", code=code, message=message)


def new_grpc_error(message: str, http_code: int) -> AppError:
    """NewGrpcError: a bare gRPC status error. sets the status detail to `http.StatusText(code)`; storing that phrase in `type` lets `to_grpc_error` emit the same wire detail."""
    from http import HTTPStatus

    try:
        text = HTTPStatus(http_code).phrase
    except ValueError:
        text = "Unknown"
    return AppError(type=text, code=http_code, message=message)


def as_app_error(err: BaseException) -> AppError:
    """Coerce any exception to an AppError (unknown -> 500)."""
    if isinstance(err, AppError):
        return err
    return new_internal_error(err)


def error_chain(err: BaseException) -> list[str]:
    """Render the cause chain for logs without leaking it to clients."""
    parts: list[str] = []
    seen: set[int] = set()
    current: BaseException | None = err
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        parts.append(f"{type(current).__name__}: {current}")
        current = current.__cause__ or current.__context__
    return parts


__all__ = [
    "AppError",
    "ErrorType",
    "ValidationError",
    "err_bad_request",
    "err_validation_failed",
    "err_unauthorized",
    "err_forbidden",
    "err_not_found",
    "err_conflict",
    "err_too_many_requests",
    "err_internal",
    "err_service_unavailable",
    "err_timeout",
    "err_user_not_found",
    "err_role_not_found",
    "err_token_not_found",
    "err_find_by_user_id",
    "err_parse_date",
    "err_failed",
    "err_not_found_response",
    "err_no_rows_or_failed",
    "err_constraint_or_failed",
    "new_bad_request_error",
    "new_not_found_error",
    "new_conflict_error",
    "new_internal_error",
    "new_service_unavailable_error",
    "new_forbidden_error",
    "new_unauthorized_error",
    "new_validation_error",
    "new_error_response",
    "new_grpc_error",
    "as_app_error",
    "error_chain",
    "is_valid_http_code",
]
