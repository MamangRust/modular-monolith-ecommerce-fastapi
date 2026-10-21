"""Role service"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.auth import UserRole
from pkg.database.schema.role import GetActiveRolesRow, GetRolesRow, Role
from shared.domain.requests.auth import CreateUserRoleRequest


class RoleQueryService(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetRolesRow], int]: ...

    async def find_by_id(self, role_id: int) -> Role: ...

    async def find_by_name(self, role_name: str) -> Role: ...

    async def find_by_user_id(self, user_id: int) -> list[Role]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetActiveRolesRow], int]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetActiveRolesRow], int]: ...


class RoleCommandService(Protocol):
    async def create(self, role_name: str) -> Role: ...

    async def update(self, role_id: int, role_name: str) -> Role: ...

    async def trash(self, role_id: int) -> Role: ...

    async def restore(self, role_id: int) -> Role: ...

    async def delete_permanent(self, role_id: int) -> None: ...

    async def restore_all(self) -> None: ...

    async def delete_all_permanent(self) -> None: ...

    async def assign_role_to_user(self, request: CreateUserRoleRequest) -> UserRole: ...


__all__ = ["RoleCommandService", "RoleQueryService"]
