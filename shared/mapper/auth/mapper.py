"""Auth response mapping. The gRPC handler already formats timestamps into the wire shape (`time.Time.String`), so the mapper passes `created_at`/`updated_at` through unchanged rather than reformatting. mapper dereferences `res.Data` unconditionally (a nil `Data` would panic); protobuf sub-messages are never None in Python, so the equivalent failure mode is an empty string rather than a panic. No behaviour worth reproducing here."""

from __future__ import annotations

from typing import Any

from shared.domain.response.auth import (
    ApiResponseForgotPassword,
    ApiResponseGetMe,
    ApiResponseLogin,
    ApiResponseRefreshToken,
    ApiResponseRegister,
    ApiResponseResetPassword,
    ApiResponseVerifyCode,
    TokenResponse,
)
from shared.domain.response.user import UserResponse


def _map_user(pb: Any) -> UserResponse:
    return UserResponse(
        id=int(pb.id),
        firstname=pb.firstname,
        lastname=pb.lastname,
        email=pb.email,
        is_verified=False,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def _map_token(pb: Any) -> TokenResponse:
    return TokenResponse(
        access_token=pb.access_token,
        refresh_token=pb.refresh_token,
    )


def to_response_verify_code(pb: Any) -> ApiResponseVerifyCode:
    return ApiResponseVerifyCode(status=pb.status, message=pb.message)


def to_response_forgot_password(pb: Any) -> ApiResponseForgotPassword:
    return ApiResponseForgotPassword(status=pb.status, message=pb.message)


def to_response_reset_password(pb: Any) -> ApiResponseResetPassword:
    return ApiResponseResetPassword(status=pb.status, message=pb.message)


def to_response_login(pb: Any) -> ApiResponseLogin:
    return ApiResponseLogin(
        status=pb.status, message=pb.message, data=_map_token(pb.data)
    )


def to_response_register(pb: Any) -> ApiResponseRegister:
    return ApiResponseRegister(
        status=pb.status, message=pb.message, data=_map_user(pb.data)
    )


def to_response_refresh_token(pb: Any) -> ApiResponseRefreshToken:
    return ApiResponseRefreshToken(
        status=pb.status, message=pb.message, data=_map_token(pb.data)
    )


def to_response_get_me(pb: Any) -> ApiResponseGetMe:
    return ApiResponseGetMe(
        status=pb.status, message=pb.message, data=_map_user(pb.data)
    )


__all__ = [
    "to_response_forgot_password",
    "to_response_get_me",
    "to_response_login",
    "to_response_refresh_token",
    "to_response_register",
    "to_response_reset_password",
    "to_response_verify_code",
]
