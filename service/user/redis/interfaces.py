"""User cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.user import (
    GetActiveUsersRow,
    GetUserByIDRow,
    GetUsersRow,
)


class UserQueryCache(Protocol):
    async def get_users(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetUsersRow], int] | None: ...

    async def set_users(
        self, page: int, page_size: int, search: str, users: list[GetUsersRow], total: int
    ) -> None: ...

    async def get_user_by_id(self, user_id: int) -> GetUserByIDRow | None: ...

    async def set_user_by_id(self, user: GetUserByIDRow) -> None: ...

    async def get_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetActiveUsersRow], int] | None: ...

    async def set_active(
        self,
        page: int,
        page_size: int,
        search: str,
        users: list[GetActiveUsersRow],
        total: int,
    ) -> None: ...

    async def get_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetActiveUsersRow], int] | None: ...

    async def set_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        users: list[GetActiveUsersRow],
        total: int,
    ) -> None: ...


class UserCommandCache(Protocol):
    async def delete_cached_user(self, user_id: int) -> int: ...

    async def invalidate_lists(self) -> int: ...

    async def invalidate_user(self, user_id: int) -> int: ...

    async def invalidate_all(self) -> int: ...


__all__ = ["UserCommandCache", "UserQueryCache"]
