"""Unit tests for the auth gRPC handler (in-process, no server/DB). Also pins `go_time_string`, which reproduces for the auth domain's Register/GetMe timestamps — a different wire shape from the user domain's RFC3339 and the role domain's date-only output."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import grpc
import pytest

from pb.auth import auth_pb2
from pkg.database.schema.auth import AuthCreateUserRow
from pkg.database.schema.user import GetUserByIDRow
from pkg.logger.logger import Logger
from service.auth.handler.auth import AuthHandler, go_time_string
from shared.domain.requests.auth import CreateResetPasswordRequest, RegisterRequest
from shared.domain.response.auth import TokenResponse
from shared.errors import AppError

CREATED = datetime(2026, 8, 19, 10, 0, 0)
UPDATED = datetime(2026, 8, 19, 10, 0, 1)


class FakeAbort(Exception):
    def __init__(self, code: grpc.StatusCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class FakeContext:
    def __init__(self) -> None:
        self.aborted: FakeAbort | None = None

    def set_trailing_metadata(self, metadata: tuple[Any, ...]) -> None:
        pass

    async def abort(self, code: grpc.StatusCode, message: str) -> None:
        self.aborted = FakeAbort(code, message)
        raise self.aborted


class FakeRegisterService:
    def __init__(self) -> None:
        self.requests: list[RegisterRequest] = []
        self.error: AppError | None = None

    async def register(self, request):
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return AuthCreateUserRow(
            9, "John", "Doe", "john@example.com", "h", CREATED, UPDATED
        )


class FakeLoginService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.error: AppError | None = None

    async def login(self, request):
        self.calls.append((request.email, request.password))
        if self.error is not None:
            raise self.error
        return TokenResponse(access_token="access-1", refresh_token="refresh-1")


class FakePasswordResetService:
    def __init__(self) -> None:
        self.forgot: list[str] = []
        self.reset: list[CreateResetPasswordRequest] = []
        self.codes: list[str] = []
        self.error: AppError | None = None

    async def forgot_password(self, email):
        self.forgot.append(email)
        if self.error is not None:
            raise self.error
        return True

    async def reset_password(self, request):
        self.reset.append(request)
        if self.error is not None:
            raise self.error
        return True

    async def verify_code(self, code):
        self.codes.append(code)
        if self.error is not None:
            raise self.error
        return True


class FakeIdentifyService:
    def __init__(self) -> None:
        self.refreshed: list[str] = []
        self.me: list[int] = []
        self.error: AppError | None = None

    async def refresh_token(self, token):
        self.refreshed.append(token)
        if self.error is not None:
            raise self.error
        return TokenResponse(access_token="access-2", refresh_token="refresh-2")

    async def get_me(self, user_id):
        self.me.append(user_id)
        if self.error is not None:
            raise self.error
        return GetUserByIDRow(
            user_id, "John", "Doe", "john@example.com", "h", CREATED, UPDATED
        )


def _handler() -> tuple[AuthHandler, dict[str, Any]]:
    register = FakeRegisterService()
    login = FakeLoginService()
    password_reset = FakePasswordResetService()
    identify = FakeIdentifyService()
    handler = AuthHandler(
        register, login, password_reset, identify, Logger("test", "error")
    )
    return handler, {
        "register": register,
        "login": login,
        "password_reset": password_reset,
        "identify": identify,
    }


# ---- go_time_string ----


def test_go_time_string_matches_go_shapes() -> None:
    assert go_time_string(None) == ""
    assert go_time_string(datetime(2026, 8, 19, 10, 0, 0)) == (
        "2026-08-19 10:00:00 +0000 UTC"
    )
    assert go_time_string(datetime(2026, 8, 19, 10, 0, 0, 500000)) == (
        "2026-08-19 10:00:00.5 +0000 UTC"
    )
    assert go_time_string(datetime(2026, 8, 19, 10, 0, 0, 123456)) == (
        "2026-08-19 10:00:00.123456 +0000 UTC"
    )


def test_go_time_string_honours_non_utc_offsets() -> None:
    aware = datetime(2026, 8, 19, 10, 0, 0, tzinfo=timezone(timedelta(hours=7)))
    assert go_time_string(aware) == "2026-08-19 10:00:00 +0700 UTC+07:00"


# ---- RPCs ----


async def test_verify_code_returns_go_message() -> None:
    handler, fakes = _handler()
    response = await handler.VerifyCode(
        auth_pb2.VerifyCodeRequest(code="abc"), FakeContext()
    )
    assert response.status == "success"
    assert response.message == "Verification successfully"
    assert fakes["password_reset"].codes == ["abc"]


async def test_forgot_password_returns_go_message() -> None:
    handler, fakes = _handler()
    response = await handler.ForgotPassword(
        auth_pb2.ForgotPasswordRequest(email="john@example.com"), FakeContext()
    )
    assert response.message == "ForgotPassword successful"
    assert fakes["password_reset"].forgot == ["john@example.com"]


async def test_reset_password_builds_service_request() -> None:
    handler, fakes = _handler()
    response = await handler.ResetPassword(
        auth_pb2.ResetPasswordRequest(
            reset_token="tok", password="secret2", confirm_password="secret2"
        ),
        FakeContext(),
    )
    assert response.message == "Reset password successful"
    sent = fakes["password_reset"].reset[0]
    assert (sent.reset_token, sent.password, sent.confirm_password) == (
        "tok",
        "secret2",
        "secret2",
    )


async def test_login_user_returns_token_pair() -> None:
    handler, fakes = _handler()
    response = await handler.LoginUser(
        auth_pb2.LoginRequest(email="john@example.com", password="secret1"),
        FakeContext(),
    )
    # spelling ("successfull") is preserved verbatim.
    assert response.message == "LoginUser successfull"
    assert response.data.access_token == "access-1"
    assert response.data.refresh_token == "refresh-1"
    assert fakes["login"].calls == [("john@example.com", "secret1")]


async def test_refresh_token_returns_new_token() -> None:
    """Deviation: echoed the presented (already-deleted) token."""
    handler, fakes = _handler()
    response = await handler.RefreshToken(
        auth_pb2.RefreshTokenRequest(refresh_token="old"), FakeContext()
    )
    assert response.message == "Refresh token successful"
    assert response.data.refresh_token == "refresh-2"
    assert fakes["identify"].refreshed == ["old"]


async def test_get_me_formats_timestamps_with_go_shape() -> None:
    handler, fakes = _handler()
    response = await handler.GetMe(auth_pb2.GetMeRequest(userId=4), FakeContext())
    assert response.message == "Get me successfully"
    assert response.data.id == 4
    assert response.data.created_at == "2026-08-19 10:00:00 +0000 UTC"
    assert response.data.updated_at == "2026-08-19 10:00:01 +0000 UTC"
    assert fakes["identify"].me == [4]


async def test_register_user_formats_timestamps_with_go_shape() -> None:
    handler, fakes = _handler()
    response = await handler.RegisterUser(
        auth_pb2.RegisterRequest(
            firstname="John",
            lastname="Doe",
            email="john@example.com",
            password="secret1",
            confirm_password="secret1",
        ),
        FakeContext(),
    )
    assert response.message == "RegisterUser successful"
    assert response.data.email == "john@example.com"
    assert response.data.created_at == "2026-08-19 10:00:00 +0000 UTC"
    sent = fakes["register"].requests[0]
    assert sent.email == "john@example.com"


async def test_app_error_maps_to_grpc_status() -> None:
    handler, fakes = _handler()
    fakes["login"].error = AppError("UNAUTHORIZED", 401, "Password does not match")
    context = FakeContext()

    with pytest.raises(FakeAbort) as excinfo:
        await handler.LoginUser(
            auth_pb2.LoginRequest(email="john@example.com", password="wrongpass"),
            context,
        )

    assert excinfo.value.code is grpc.StatusCode.UNAUTHENTICATED
    assert context.aborted is not None
