"""Role query cache. Deviation from (recorded in the matrix): wrote the active list cache but never read it, so those entries were dead. reads it like every other list cache."""

from __future__ import annotations

from pkg.database.schema.role import GetActiveRolesRow, GetRolesRow, Role
from pkg.logger.logger import Logger
from service.role.redis.cache import (
    active_row_from_dict,
    active_row_to_dict,
    role_from_dict,
    role_to_dict,
    roles_row_from_dict,
    roles_row_to_dict,
)
from service.role.redis.common import (
    TTL_DEFAULT,
    role_active_key,
    role_all_key,
    role_by_id_key,
    role_by_user_id_key,
    role_trashed_key,
)
from shared.cache import CacheStore


class RoleQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_roles(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetRolesRow], int] | None:
        payload = await self._store.get_json(role_all_key(page, page_size, search))
        return _decode_page(payload, roles_row_from_dict)

    async def set_roles(
        self, page: int, page_size: int, search: str, roles: list[GetRolesRow], total: int
    ) -> None:
        await self._store.set_json(
            role_all_key(page, page_size, search),
            _encode_page(roles, total, roles_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_role_by_id(self, role_id: int) -> Role | None:
        payload = await self._store.get_json(role_by_id_key(role_id))
        if not isinstance(payload, dict):
            return None
        return role_from_dict(payload)

    async def set_role_by_id(self, role: Role) -> None:
        await self._store.set_json(role_by_id_key(role.role_id), role_to_dict(role), TTL_DEFAULT)

    async def get_role_by_user_id(self, user_id: int) -> list[Role] | None:
        payload = await self._store.get_json(role_by_user_id_key(user_id))
        if not isinstance(payload, list):
            return None
        return [role_from_dict(item) for item in payload]

    async def set_role_by_user_id(self, user_id: int, roles: list[Role]) -> None:
        await self._store.set_json(
            role_by_user_id_key(user_id),
            [role_to_dict(role) for role in roles],
            TTL_DEFAULT,
        )

    async def get_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetActiveRolesRow], int] | None:
        payload = await self._store.get_json(role_active_key(page, page_size, search))
        return _decode_page(payload, active_row_from_dict)

    async def set_active(
        self,
        page: int,
        page_size: int,
        search: str,
        roles: list[GetActiveRolesRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            role_active_key(page, page_size, search),
            _encode_page(roles, total, active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetActiveRolesRow], int] | None:
        payload = await self._store.get_json(role_trashed_key(page, page_size, search))
        return _decode_page(payload, active_row_from_dict)

    async def set_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        roles: list[GetActiveRolesRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            role_trashed_key(page, page_size, search),
            _encode_page(roles, total, active_row_to_dict),
            TTL_DEFAULT,
        )


def _encode_page(rows: list, total: int, to_dict) -> dict:
    return {"data": [to_dict(row) for row in rows], "total_records": total}


def _decode_page(payload, from_dict):
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    total = int(payload.get("total_records") or 0)
    return [from_dict(item, total) for item in data], total


__all__ = ["RoleQueryCacheImpl"]
