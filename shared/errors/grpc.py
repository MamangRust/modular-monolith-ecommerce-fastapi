"""Application error <-> gRPC status conversion. attaches `pb.common.ErrorResponse` through `status.WithDetails`, which on the wire becomes the reserved `grpc-status-details-bin` trailing metadata holding a serialized `google.rpc.Status`. emits and reads exactly that envelope, so a client and a Python client interoperate and the HTTP code survives the hop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NoReturn, Protocol

import grpc
from google.rpc import status_pb2

from pb.common import api_pb2
from shared.errors.core import (
    AppError,
    ErrorType,
    as_app_error,
    is_valid_http_code,
)

STATUS_DETAILS_KEY = "grpc-status-details-bin"

_HTTP_TO_GRPC: dict[int, grpc.StatusCode] = {
    400: grpc.StatusCode.INVALID_ARGUMENT,
    401: grpc.StatusCode.UNAUTHENTICATED,
    403: grpc.StatusCode.PERMISSION_DENIED,
    404: grpc.StatusCode.NOT_FOUND,
    409: grpc.StatusCode.ALREADY_EXISTS,
    429: grpc.StatusCode.RESOURCE_EXHAUSTED,
    504: grpc.StatusCode.DEADLINE_EXCEEDED,
    503: grpc.StatusCode.UNAVAILABLE,
}

_GRPC_TO_HTTP: dict[grpc.StatusCode, int] = {
    grpc.StatusCode.INVALID_ARGUMENT: 400,
    grpc.StatusCode.UNAUTHENTICATED: 401,
    grpc.StatusCode.PERMISSION_DENIED: 403,
    grpc.StatusCode.NOT_FOUND: 404,
    grpc.StatusCode.ALREADY_EXISTS: 409,
    grpc.StatusCode.RESOURCE_EXHAUSTED: 429,
    grpc.StatusCode.DEADLINE_EXCEEDED: 504,
    grpc.StatusCode.UNAVAILABLE: 503,
}

_GRPC_TO_TYPE: dict[grpc.StatusCode, str] = {
    grpc.StatusCode.INVALID_ARGUMENT: ErrorType.BAD_REQUEST.value,
    grpc.StatusCode.UNAUTHENTICATED: ErrorType.UNAUTHORIZED.value,
    grpc.StatusCode.PERMISSION_DENIED: ErrorType.FORBIDDEN.value,
    grpc.StatusCode.NOT_FOUND: ErrorType.NOT_FOUND.value,
    grpc.StatusCode.ALREADY_EXISTS: ErrorType.CONFLICT.value,
    grpc.StatusCode.RESOURCE_EXHAUSTED: ErrorType.BAD_REQUEST.value,
    grpc.StatusCode.DEADLINE_EXCEEDED: ErrorType.TIMEOUT.value,
    grpc.StatusCode.UNAVAILABLE: ErrorType.UNAVAILABLE.value,
}


@dataclass(frozen=True)
class GrpcError:
    code: grpc.StatusCode
    message: str
    detail: api_pb2.ErrorResponse | None = None


def http_to_grpc_code(code: int) -> grpc.StatusCode:
    return _HTTP_TO_GRPC.get(code, grpc.StatusCode.INTERNAL)


def grpc_to_http_code(code: grpc.StatusCode) -> int:
    return _GRPC_TO_HTTP.get(code, 500)


def grpc_to_error_type(code: grpc.StatusCode) -> str:
    return _GRPC_TO_TYPE.get(code, ErrorType.INTERNAL.value)


def to_grpc_error(err: BaseException) -> GrpcError:
    if not isinstance(err, AppError):
        return GrpcError(grpc.StatusCode.INTERNAL, "Internal server error")
    return GrpcError(
        code=http_to_grpc_code(err.code),
        message=err.message,
        detail=api_pb2.ErrorResponse(
            status=err.type,
            message=err.message,
            code=err.code,
        ),
    )


def status_bytes(detail: api_pb2.ErrorResponse, code: grpc.StatusCode, message: str) -> bytes:
    """Serialize a `google.rpc.Status` carrying the ErrorResponse detail."""
    status = status_pb2.Status(code=code.value[0], message=message)
    status.details.add().Pack(detail)
    return status.SerializeToString()


class AbortableContext(Protocol):

    def set_trailing_metadata(self, metadata: Any) -> None: ...

    async def abort(self, code: grpc.StatusCode, details: str) -> NoReturn: ...


async def abort_with_error(context: AbortableContext, err: BaseException) -> NoReturn:
    """Abort a grpc.aio handler with the mapped status + ErrorResponse detail."""
    grpc_error = to_grpc_error(err)
    if grpc_error.detail is not None:
        context.set_trailing_metadata(
            (
                (
                    STATUS_DETAILS_KEY,
                    status_bytes(grpc_error.detail, grpc_error.code, grpc_error.message),
                ),
            )
        )
    await context.abort(grpc_error.code, grpc_error.message)
    raise RuntimeError("grpc context.abort returned without raising")


def _detail_from_trailing_metadata(metadata: Any) -> api_pb2.ErrorResponse | None:
    for key, value in metadata or ():
        if key != STATUS_DETAILS_KEY:
            continue
        raw = value.encode("latin-1") if isinstance(value, str) else value
        try:
            status = status_pb2.Status.FromString(raw)
        except Exception:
            return None
        for any_detail in status.details:
            response = api_pb2.ErrorResponse()
            try:
                if any_detail.Unpack(response):
                    return response
            except Exception:
                continue
    return None


def parse_grpc_error(err: BaseException) -> AppError:
    """ParseGrpcError. Prefers the ErrorResponse detail (preserving the HTTP code), and falls back to the gRPC status code mapping when no detail is present."""
    code = getattr(err, "code", None)
    if not callable(code):
        return as_app_error(err)
    status_code = code()
    if not isinstance(status_code, grpc.StatusCode):
        return as_app_error(err)

    metadata_fn = getattr(err, "trailing_metadata", None)
    detail = _detail_from_trailing_metadata(metadata_fn() if callable(metadata_fn) else None)
    if detail is not None:
        http_code = int(detail.code)
        if not is_valid_http_code(http_code):
            http_code = grpc_to_http_code(status_code)
        return AppError(type=detail.status, code=http_code, message=detail.message)

    details_fn = getattr(err, "details", None)
    message = details_fn() if callable(details_fn) else None
    return AppError(
        type=grpc_to_error_type(status_code),
        code=grpc_to_http_code(status_code),
        message=message or status_code.name,
    )


__all__ = [
    "GrpcError",
    "STATUS_DETAILS_KEY",
    "abort_with_error",
    "grpc_to_error_type",
    "grpc_to_http_code",
    "http_to_grpc_code",
    "parse_grpc_error",
    "status_bytes",
    "to_grpc_error",
]
