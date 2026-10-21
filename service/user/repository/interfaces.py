"""User repository the `RoleRepository` is deliberately not: it is constructed and injected into the command service but never called, so carrying it here would be dead code."""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.user import (
    CreateUserRow,
    GetActiveUsersRow,
    GetUserByEmailRow,
    GetUserByIDRow,
    GetUsersRow,
    RestoreUserRow,
    TrashUserRow,
    UpdateUserRow,
)


class UserQueryRepository(Protocol):
    async def find_all(self, search: str, page: int, page_size: int) -> list[GetUsersRow]: ...

    async def find_by_id(self, user_id: int) -> GetUserByIDRow: ...

    async def find_by_email(self, email: str) -> GetUserByEmailRow: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetActiveUsersRow]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetActiveUsersRow]: ...


class UserCommandRepository(Protocol):
    async def create(
        self, firstname: str, lastname: str, email: str, hashed_password: str
    ) -> CreateUserRow: ...

    async def update(
        self, user_id: int, firstname: str, lastname: str, email: str, hashed_password: str
    ) -> UpdateUserRow: ...

    async def trash(self, user_id: int) -> TrashUserRow: ...

    async def restore(self, user_id: int) -> RestoreUserRow: ...

    async def delete_permanent(self, user_id: int) -> None: ...

    async def restore_all(self) -> None: ...

    async def delete_all_permanent(self) -> None: ...


__all__ = ["UserCommandRepository", "UserQueryRepository"]
