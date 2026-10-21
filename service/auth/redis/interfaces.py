"""Auth cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.user import GetUserByIDRow
from shared.domain.response.auth import TokenResponse


class IdentityCache(Protocol):
    async def set_refresh_token(self, token: str, ttl_seconds: int) -> None: ...

    async def get_refresh_token(self, token: str) -> tuple[str, bool]: ...

    async def delete_refresh_token(self, token: str) -> None: ...

    async def set_cached_user_info(
        self, user: GetUserByIDRow, ttl_seconds: int
    ) -> None: ...

    async def get_cached_user_info(
        self, user_id: str | int
    ) -> GetUserByIDRow | None: ...

    async def delete_cached_user_info(self, user_id: str | int) -> None: ...


class LoginCache(Protocol):
    async def get_cached_login(self, email: str) -> TokenResponse | None: ...

    async def set_cached_login(
        self, email: str, data: TokenResponse, ttl_seconds: int
    ) -> None: ...

    async def increment_failed_login(self, email: str) -> int: ...

    async def reset_failed_login(self, email: str) -> None: ...

    async def is_account_locked(self, email: str) -> bool: ...


class PasswordResetCache(Protocol):
    async def set_reset_token_cache(
        self, token: str, user_id: int, ttl_seconds: int
    ) -> None: ...

    async def get_reset_token_cache(self, token: str) -> tuple[int, bool]: ...

    async def delete_reset_token_cache(self, token: str) -> None: ...

    async def delete_verification_code_cache(self, email: str) -> None: ...


class RegisterCache(Protocol):
    async def set_verification_code_cache(
        self, email: str, code: str, ttl_seconds: int
    ) -> None: ...


__all__ = [
    "IdentityCache",
    "LoginCache",
    "PasswordResetCache",
    "RegisterCache",
]
