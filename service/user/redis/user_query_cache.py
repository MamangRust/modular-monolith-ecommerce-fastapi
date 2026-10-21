"""User query cache."""

from __future__ import annotations

from pkg.database.schema.user import (
    GetActiveUsersRow,
    GetUserByIDRow,
    GetUsersRow,
)
from pkg.logger.logger import Logger
from service.user.redis.cache import (
    active_row_from_dict,
    active_row_to_dict,
    user_row_from_dict,
    user_row_to_dict,
    users_row_from_dict,
    users_row_to_dict,
)
from service.user.redis.common import (
    TTL_DEFAULT,
    user_active_key,
    user_all_key,
    user_by_id_key,
    user_trashed_key,
)
from shared.cache import CacheStore


class UserQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_users(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetUsersRow], int] | None:
        payload = await self._store.get_json(user_all_key(page, page_size, search))
        return _decode_page(payload, users_row_from_dict)

    async def set_users(
        self, page: int, page_size: int, search: str, users: list[GetUsersRow], total: int
    ) -> None:
        await self._store.set_json(
            user_all_key(page, page_size, search),
            _encode_page(users, total, users_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_user_by_id(self, user_id: int) -> GetUserByIDRow | None:
        payload = await self._store.get_json(user_by_id_key(user_id))
        if not isinstance(payload, dict):
            return None
        return user_row_from_dict(payload)

    async def set_user_by_id(self, user: GetUserByIDRow) -> None:
        await self._store.set_json(
            user_by_id_key(user.user_id), user_row_to_dict(user), TTL_DEFAULT
        )

    async def get_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetActiveUsersRow], int] | None:
        payload = await self._store.get_json(user_active_key(page, page_size, search))
        return _decode_page(payload, active_row_from_dict)

    async def set_active(
        self,
        page: int,
        page_size: int,
        search: str,
        users: list[GetActiveUsersRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            user_active_key(page, page_size, search),
            _encode_page(users, total, active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetActiveUsersRow], int] | None:
        payload = await self._store.get_json(user_trashed_key(page, page_size, search))
        return _decode_page(payload, active_row_from_dict)

    async def set_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        users: list[GetActiveUsersRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            user_trashed_key(page, page_size, search),
            _encode_page(users, total, active_row_to_dict),
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


__all__ = ["UserQueryCacheImpl"]
