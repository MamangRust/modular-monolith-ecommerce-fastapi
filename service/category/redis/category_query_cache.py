"""Category query cache.

Reads/writes never raise: `CacheStore` swallows Redis errors so a cache
outage degrades to a DB read."""

from __future__ import annotations

from pkg.database.schema.category import (
    GetCategoriesActiveRow,
    GetCategoriesRow,
    GetCategoryByIDRow,
)
from pkg.logger.logger import Logger
from service.category.redis.cache import (
    active_row_from_dict,
    active_row_to_dict,
    category_by_id_from_dict,
    category_by_id_to_dict,
    category_row_from_dict,
    category_row_to_dict,
)
from service.category.redis.common import (
    TTL_DEFAULT,
    category_active_key,
    category_all_key,
    category_by_id_key,
    category_trashed_key,
)
from shared.cache import CacheStore


class CategoryQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_categories(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetCategoriesRow], int] | None:
        payload = await self._store.get_json(category_all_key(page, page_size, search))
        return _decode_page(payload, category_row_from_dict)

    async def set_categories(
        self,
        page: int,
        page_size: int,
        search: str,
        categories: list[GetCategoriesRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            category_all_key(page, page_size, search),
            _encode_page(categories, total, category_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_category_by_id(self, category_id: int) -> GetCategoryByIDRow | None:
        payload = await self._store.get_json(category_by_id_key(category_id))
        if not isinstance(payload, dict):
            return None
        return category_by_id_from_dict(payload)

    async def set_category_by_id(self, category: GetCategoryByIDRow) -> None:
        await self._store.set_json(
            category_by_id_key(category.category_id),
            category_by_id_to_dict(category),
            TTL_DEFAULT,
        )

    async def get_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetCategoriesActiveRow], int] | None:
        payload = await self._store.get_json(
            category_active_key(page, page_size, search)
        )
        return _decode_page(payload, active_row_from_dict)

    async def set_active(
        self,
        page: int,
        page_size: int,
        search: str,
        categories: list[GetCategoriesActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            category_active_key(page, page_size, search),
            _encode_page(categories, total, active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetCategoriesActiveRow], int] | None:
        payload = await self._store.get_json(
            category_trashed_key(page, page_size, search)
        )
        return _decode_page(payload, active_row_from_dict)

    async def set_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        categories: list[GetCategoriesActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            category_trashed_key(page, page_size, search),
            _encode_page(categories, total, active_row_to_dict),
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


__all__ = ["CategoryQueryCacheImpl"]
