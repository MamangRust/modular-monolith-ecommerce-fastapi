"""Auth service"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.auth import AuthCreateUserRow
from pkg.database.schema.user import GetUserByIDRow
from shared.domain.requests.auth import (
    AuthRequest,
    CreateResetPasswordRequest,
    RegisterRequest,
)
from shared.domain.response.auth import TokenResponse


class RegistrationService(Protocol):
    async def register(self, request: RegisterRequest) -> AuthCreateUserRow: ...


class LoginService(Protocol):
    async def login(self, request: AuthRequest) -> TokenResponse: ...


class PasswordResetService(Protocol):
    async def forgot_password(self, email: str) -> bool: ...

    async def reset_password(self, request: CreateResetPasswordRequest) -> bool: ...

    async def verify_code(self, code: str) -> bool: ...


class IdentifyService(Protocol):
    async def refresh_token(self, token: str) -> TokenResponse: ...

    async def get_me(self, user_id: int) -> GetUserByIDRow: ...


__all__ = [
    "IdentifyService",
    "LoginService",
    "PasswordResetService",
    "RegistrationService",
]
