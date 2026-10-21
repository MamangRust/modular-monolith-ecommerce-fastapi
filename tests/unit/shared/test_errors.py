"""Unit tests for shared.errors: factories, DB mapping, gRPC conversion."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import grpc
import pytest
from google.rpc import status_pb2

from pb.common import api_pb2
from pkg.database.errors import NoRowsError
from shared.errors import (
    AppError,
    err_constraint_or_failed,
    err_no_rows_or_failed,
    err_role_not_found,
    new_grpc_error,
    parse_grpc_error,
    status_bytes,
    to_grpc_error,
)


class _UniqueViolation(Exception):
    sqlstate = "23505"


class _ForeignKeyViolation(Exception):
    sqlstate = "23503"


def test_no_rows_maps_to_404() -> None:
    err = err_no_rows_or_failed(NoRowsError(), "Role", "find role")
    assert err.code == 404
    assert err.message == "Role not found"


def test_unknown_error_maps_to_500() -> None:
    err = err_no_rows_or_failed(RuntimeError("boom"), "Role", "find role")
    assert err.code == 500
    assert err.message == "Failed to find role"


def test_unique_violation_maps_to_409() -> None:
    err = err_constraint_or_failed(_UniqueViolation(), "Role", "create role")
    assert err.code == 409
    assert err.message == "Role already exists"


def test_foreign_key_violation_maps_to_400() -> None:
    err = err_constraint_or_failed(_ForeignKeyViolation(), "Role", "create role")
    assert err.code == 400
    assert err.message == "invalid related Role reference"


def test_to_grpc_error_preserves_code_and_detail() -> None:
    converted = to_grpc_error(err_role_not_found)
    assert converted.code is grpc.StatusCode.NOT_FOUND
    assert converted.message == "role not found"
    assert converted.detail is not None
    assert converted.detail.status == "NOT_FOUND"
    assert converted.detail.code == 404


def test_to_grpc_error_unknown_is_internal_without_detail() -> None:
    converted = to_grpc_error(RuntimeError("boom"))
    assert converted.code is grpc.StatusCode.INTERNAL
    assert converted.detail is None


def test_new_grpc_error_uses_http_reason_phrase() -> None:
    converted = to_grpc_error(new_grpc_error("Invalid Role ID", 400))
    assert converted.code is grpc.StatusCode.INVALID_ARGUMENT
    assert converted.detail is not None
    assert converted.detail.status == "Bad Request"
    assert converted.detail.code == 400


def test_status_bytes_round_trips_error_response() -> None:
    detail = api_pb2.ErrorResponse(status="NOT_FOUND", message="role not found", code=404)
    raw = status_bytes(detail, grpc.StatusCode.NOT_FOUND, "role not found")
    decoded = status_pb2.Status.FromString(raw)
    assert decoded.code == grpc.StatusCode.NOT_FOUND.value[0]
    assert decoded.message == "role not found"
    unpacked = api_pb2.ErrorResponse()
    assert decoded.details[0].Unpack(unpacked)
    assert (unpacked.status, unpacked.code) == ("NOT_FOUND", 404)


class _FakeRpcError(Exception):
    def __init__(self, code: grpc.StatusCode, message: str, raw: bytes | None = None) -> None:
        super().__init__(message)
        self._code = code
        self._message = message
        self._raw = raw

    def code(self) -> grpc.StatusCode:
        return self._code

    def details(self) -> str:
        return self._message

    def trailing_metadata(self):
        if self._raw is None:
            return ()
        return (("grpc-status-details-bin", self._raw),)


def test_parse_grpc_error_prefers_detail() -> None:
    detail = api_pb2.ErrorResponse(status="CONFLICT", message="Role already exists", code=409)
    raw = status_bytes(detail, grpc.StatusCode.ALREADY_EXISTS, "Role already exists")
    parsed = parse_grpc_error(_FakeRpcError(grpc.StatusCode.ALREADY_EXISTS, "x", raw))
    assert isinstance(parsed, AppError)
    assert parsed.code == 409
    assert parsed.type == "CONFLICT"


def test_parse_grpc_error_falls_back_to_code_mapping() -> None:
    parsed = parse_grpc_error(_FakeRpcError(grpc.StatusCode.NOT_FOUND, "missing"))
    assert parsed.code == 404
    assert parsed.type == "NOT_FOUND"
    assert parsed.message == "missing"


def test_parse_grpc_error_on_plain_exception_is_500() -> None:
    parsed = parse_grpc_error(RuntimeError("boom"))
    assert parsed.code == 500


@pytest.mark.parametrize(
    ("code", "status"),
    [
        (400, grpc.StatusCode.INVALID_ARGUMENT),
        (401, grpc.StatusCode.UNAUTHENTICATED),
        (403, grpc.StatusCode.PERMISSION_DENIED),
        (404, grpc.StatusCode.NOT_FOUND),
        (409, grpc.StatusCode.ALREADY_EXISTS),
        (429, grpc.StatusCode.RESOURCE_EXHAUSTED),
        (503, grpc.StatusCode.UNAVAILABLE),
        (504, grpc.StatusCode.DEADLINE_EXCEEDED),
        (418, grpc.StatusCode.INTERNAL),
    ],
)
def test_http_to_grpc_mapping(code: int, status: grpc.StatusCode) -> None:
    assert to_grpc_error(AppError("X", code, "m")).code is status


def test_app_error_survives_context_manager_reraise() -> None:
    """Regression: `contextlib` re-raises with `exc.__traceback__ = tb`.

    A strictly frozen exception turned that assignment into a
    FrozenInstanceError, so any AppError raised inside a `with` block
    surfaced as a 500 instead of its real code.
    """
    from contextlib import contextmanager

    @contextmanager
    def span():
        yield None

    with pytest.raises(AppError) as excinfo:
        with span():
            raise err_role_not_found

    assert excinfo.value.code == 404
    assert excinfo.value.type == "NOT_FOUND"


def test_app_error_still_rejects_data_field_mutation() -> None:
    with pytest.raises(FrozenInstanceError):
        err_role_not_found.message = "nope"  # type: ignore[misc]
