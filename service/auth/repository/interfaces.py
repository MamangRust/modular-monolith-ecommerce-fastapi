"""Auth repository Unlike the user domain, every interface here is actually consumed: the register service needs Role + UserRole, login/identify need RefreshToken, and password-reset needs ResetToken."""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.auth import (
    AuthCreateUserRow,
    CreateResetTokenRow,
    GetResetTokenRow,
    GetUserByEmailAndVerifiedRow,
    GetUserByVerificationCodeRow,
    RefreshToken,
    UpdateUserIsVerifiedRow,
    UserRole,
)
from pkg.database.schema.role import Role
from pkg.database.schema.user import GetUserByEmailRow, GetUserByIDRow
from shared.domain.requests.auth import (
    CreateRefreshToken,
    CreateResetTokenRequest,
    CreateUserRoleRequest,
    RegisterRequest,
    RemoveUserRoleRequest,
    UpdateRefreshToken,
)


class UserRepository(Protocol):
    async def find_by_id(self, user_id: int) -> GetUserByIDRow: ...

    async def find_by_email(self, email: str) -> GetUserByEmailRow: ...

    async def find_by_email_and_verify(
        self, email: str
    ) -> GetUserByEmailAndVerifiedRow: ...

    async def find_by_verification_code(
        self, verification_code: str
    ) -> GetUserByVerificationCodeRow | None: ...

    async def create_user(self, request: RegisterRequest) -> AuthCreateUserRow: ...

    async def update_user_is_verified(
        self, user_id: int, is_verified: bool
    ) -> UpdateUserIsVerifiedRow: ...

    async def update_user_password(
        self, user_id: int, password: str
    ) -> UpdateUserIsVerifiedRow: ...


class ResetTokenRepository(Protocol):
    async def find_by_token(self, code: str) -> GetResetTokenRow: ...

    async def create_reset_token(
        self, request: CreateResetTokenRequest
    ) -> CreateResetTokenRow: ...

    async def delete_reset_token(self, user_id: int) -> None: ...


class RefreshTokenRepository(Protocol):
    async def find_by_token(self, token: str) -> RefreshToken: ...

    async def find_by_user_id(self, user_id: int) -> RefreshToken: ...

    async def create_refresh_token(self, request: CreateRefreshToken) -> RefreshToken: ...

    async def update_refresh_token(self, request: UpdateRefreshToken) -> RefreshToken: ...

    async def delete_refresh_token(self, token: str) -> None: ...

    async def delete_refresh_token_by_user_id(self, user_id: int) -> None: ...


class UserRoleRepository(Protocol):
    async def assign_role_to_user(
        self, request: CreateUserRoleRequest
    ) -> UserRole: ...

    async def remove_role_from_user(
        self, request: RemoveUserRoleRequest
    ) -> None: ...


class RoleRepository(Protocol):
    async def find_by_id(self, role_id: int) -> Role: ...

    async def find_by_name(self, name: str) -> Role: ...


__all__ = [
    "RefreshTokenRepository",
    "ResetTokenRepository",
    "RoleRepository",
    "UserRepository",
    "UserRoleRepository",
]
