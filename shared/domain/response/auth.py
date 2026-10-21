"""Auth response DTOs. `TokenResponse` is the login/refresh payload. The three message-only responses (verify-code, forgot-password, reset-password) intentionally have no `data` field, matching the structs. Register/GetMe reuse `UserResponse` from the user domain, exactly as auth mapper reuses `response.UserResponse`."""

from __future__ import annotations

from dataclasses import dataclass

from shared.domain.response.responses import ApiResponse
from shared.domain.response.user import UserResponse


@dataclass
class TokenResponse:
    access_token: str
    refresh_token: str


@dataclass
class ApiResponseVerifyCode:
    status: str
    message: str


@dataclass
class ApiResponseForgotPassword:
    status: str
    message: str


@dataclass
class ApiResponseResetPassword:
    status: str
    message: str


@dataclass
class ApiResponseLogin:
    status: str
    message: str
    data: TokenResponse


@dataclass
class ApiResponseRegister:
    status: str
    message: str
    data: UserResponse


@dataclass
class ApiResponseRefreshToken:
    status: str
    message: str
    data: TokenResponse


@dataclass
class ApiResponseGetMe:
    status: str
    message: str
    data: UserResponse


# Convenience alias kept close to the name used by the gateway.
AuthApiResponse = ApiResponse[TokenResponse]


__all__ = [
    "ApiResponseForgotPassword",
    "ApiResponseGetMe",
    "ApiResponseLogin",
    "ApiResponseRefreshToken",
    "ApiResponseRegister",
    "ApiResponseResetPassword",
    "ApiResponseVerifyCode",
    "AuthApiResponse",
    "TokenResponse",
]
