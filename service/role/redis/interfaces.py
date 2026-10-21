"""Role cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.role import GetActiveRolesRow, GetRolesRow, Role


class RoleQueryCache(Protocol):
    async def get_roles(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetRolesRow], int] | None: ...

    async def set_roles(
        self, page: int, page_size: int, search: str, roles: list[GetRolesRow], total: int
    ) -> None: ...

    async def get_role_by_id(self, role_id: int) -> Role | None: ...

    async def set_role_by_id(self, role: Role) -> None: ...

    async def get_role_by_user_id(self, user_id: int) -> list[Role] | None: ...

    async def set_role_by_user_id(self, user_id: int, roles: list[Role]) -> None: ...

    async def get_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetActiveRolesRow], int] | None: ...

    async def set_active(
        self,
        page: int,
        page_size: int,
        search: str,
        roles: list[GetActiveRolesRow],
        total: int,
    ) -> None: ...

    async def get_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetActiveRolesRow], int] | None: ...

    async def set_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        roles: list[GetActiveRolesRow],
        total: int,
    ) -> None: ...


class RoleCommandCache(Protocol):
    async def delete_cached_role(self, role_id: int) -> int: ...

    async def invalidate_lists(self) -> int: ...

    async def invalidate_role(self, role_id: int) -> int: ...

    async def invalidate_all(self) -> int: ...


__all__ = ["RoleCommandCache", "RoleQueryCache"]
