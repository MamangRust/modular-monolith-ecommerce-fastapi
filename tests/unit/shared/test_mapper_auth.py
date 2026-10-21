"""Unit tests for the auth response mapper and its dataclass envelopes."""

from __future__ import annotations

from dataclasses import asdict

from pb.auth import auth_pb2
from shared.mapper.auth import (
    AuthResponseMapper,
    new_auth_response_mapper,
    to_response_forgot_password,
    to_response_get_me,
    to_response_login,
    to_response_refresh_token,
    to_response_register,
    to_response_reset_password,
    to_response_verify_code,
)


def _register() -> auth_pb2.ApiResponseRegister:
    message = auth_pb2.ApiResponseRegister(
        status="success", message="RegisterUser successful"
    )
    message.data.id = 7
    message.data.firstname = "John"
    message.data.lastname = "Doe"
    message.data.email = "john@example.com"
    message.data.created_at = "2026-08-19 10:00:00.5 +0000 UTC"
    message.data.updated_at = "2026-08-19 10:00:01 +0000 UTC"
    return message


def _token_envelope(kind: str) -> object:
    if kind == "login":
        message = auth_pb2.ApiResponseLogin(status="success", message="ok")
    else:
        message = auth_pb2.ApiResponseRefreshToken(status="success", message="ok")
    message.data.access_token = "access-1"
    message.data.refresh_token = "refresh-1"
    return message


def test_register_mapping_passes_go_timestamps_through() -> None:
    dumped = asdict(to_response_register(_register()))
    assert dumped["status"] == "success"
    assert dumped["message"] == "RegisterUser successful"
    assert dumped["data"] == {
        "id": 7,
        "firstname": "John",
        "lastname": "Doe",
        "email": "john@example.com",
        # The auth gRPC contract carries no is_verified flag, so the mapper
        # renders false just as mapper does.
        "is_verified": False,
        "created_at": "2026-08-19 10:00:00.5 +0000 UTC",
        "updated_at": "2026-08-19 10:00:01 +0000 UTC",
    }


def test_get_me_mapping() -> None:
    message = auth_pb2.ApiResponseGetMe(status="success", message="Get me successfully")
    message.data.id = 3
    message.data.firstname = "Jane"
    message.data.lastname = "Roe"
    message.data.email = "jane@example.com"
    message.data.created_at = "2026-08-19 10:00:00 +0000 UTC"
    message.data.updated_at = "2026-08-19 10:00:00 +0000 UTC"
    dumped = asdict(to_response_get_me(message))
    assert dumped["data"]["id"] == 3
    assert dumped["data"]["email"] == "jane@example.com"
    assert dumped["data"]["is_verified"] is False


def test_login_and_refresh_carry_the_token_pair() -> None:
    login = asdict(to_response_login(_token_envelope("login")))
    refresh = asdict(to_response_refresh_token(_token_envelope("refresh")))
    assert login["data"] == {"access_token": "access-1", "refresh_token": "refresh-1"}
    assert refresh["data"] == {
        "access_token": "access-1",
        "refresh_token": "refresh-1",
    }


def test_message_only_responses_have_no_data_field() -> None:
    verify = auth_pb2.ApiResponseVerifyCode(
        status="success", message="Verification successfully"
    )
    forgot = auth_pb2.ApiResponseForgotPassword(
        status="success", message="ForgotPassword successful"
    )
    reset = auth_pb2.ApiResponseResetPassword(
        status="success", message="Reset password successful"
    )

    for mapped in (
        to_response_verify_code(verify),
        to_response_forgot_password(forgot),
        to_response_reset_password(reset),
    ):
        dumped = asdict(mapped)
        assert "data" not in dumped
        assert dumped["status"] == "success"
        assert dumped["message"]


def test_mapper_bundle_matches_module_functions() -> None:
    mapper: AuthResponseMapper = new_auth_response_mapper()
    message = _register()
    assert asdict(mapper.to_response_register(message)) == asdict(
        to_response_register(message)
    )
