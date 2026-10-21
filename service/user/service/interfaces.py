"""User service"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.user import (
    CreateUserRow,
    GetActiveUsersRow,
    GetUserByIDRow,
    GetUsersRow,
    RestoreUserRow,
    TrashUserRow,
    UpdateUserRow,
)


class UserQueryService(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetUsersRow], int]: ...

    async def find_by_id(self, user_id: int) -> GetUserByIDRow: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetActiveUsersRow], int]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetActiveUsersRow], int]: ...


class UserCommandService(Protocol):
    async def create(
        self, firstname: str, lastname: str, email: str, password: str
    ) -> CreateUserRow: ...

    async def update(
        self, user_id: int, firstname: str, lastname: str, email: str, password: str
    ) -> UpdateUserRow: ...

    async def trash(self, user_id: int) -> TrashUserRow: ...

    async def restore(self, user_id: int) -> RestoreUserRow: ...

    async def delete_permanent(self, user_id: int) -> None: ...

    async def restore_all(self) -> None: ...

    async def delete_all_permanent(self) -> None: ...


__all__ = ["UserCommandService", "UserQueryService"]
