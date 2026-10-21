"""Order item query cache. Reads/writes never raise: `CacheStore` swallows Redis errors so a cache outage degrades to a DB read. The by-order setter skips empty result sets (returns early when `len(data) == 0`), so an empty list is never cached."""

from __future__ import annotations

from pkg.database.schema.order_item import (
    GetOrderItemsActiveRow,
    GetOrderItemsByOrderRow,
    GetOrderItemsRow,
    GetOrderItemsTrashedRow,
)
from pkg.logger.logger import Logger
from service.order_item.redis.cache import (
    active_row_from_dict,
    active_row_to_dict,
    by_order_row_from_dict,
    by_order_row_to_dict,
    order_item_row_from_dict,
    order_item_row_to_dict,
)
from service.order_item.redis.common import (
    TTL_DEFAULT,
    order_item_active_key,
    order_item_all_key,
    order_item_by_order_key,
    order_item_trashed_key,
)
from shared.cache import CacheStore


class OrderItemQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    async def get_order_items_all(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetOrderItemsRow], int] | None:
        payload = await self._store.get_json(
            order_item_all_key(page, page_size, search)
        )
        return _decode_page(payload, order_item_row_from_dict)

    async def set_order_items_all(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetOrderItemsRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            order_item_all_key(page, page_size, search),
            _encode_page(rows, total, order_item_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_order_item_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetOrderItemsActiveRow], int] | None:
        payload = await self._store.get_json(
            order_item_active_key(page, page_size, search)
        )
        return _decode_page(payload, active_row_from_dict)

    async def set_order_item_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetOrderItemsActiveRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            order_item_active_key(page, page_size, search),
            _encode_page(rows, total, active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_order_item_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetOrderItemsTrashedRow], int] | None:
        payload = await self._store.get_json(
            order_item_trashed_key(page, page_size, search)
        )
        return _decode_page(payload, active_row_from_dict)

    async def set_order_item_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetOrderItemsTrashedRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            order_item_trashed_key(page, page_size, search),
            _encode_page(rows, total, active_row_to_dict),
            TTL_DEFAULT,
        )

    async def get_order_items(
        self, order_id: int
    ) -> list[GetOrderItemsByOrderRow] | None:
        payload = await self._store.get_json(order_item_by_order_key(order_id))
        if not isinstance(payload, list):
            return None
        return [by_order_row_from_dict(item) for item in payload]

    async def set_order_items(self, rows: list[GetOrderItemsByOrderRow]) -> None:
        if not rows:
            return
        await self._store.set_json(
            order_item_by_order_key(rows[0].order_id),
            [by_order_row_to_dict(row) for row in rows],
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


__all__ = ["OrderItemQueryCacheImpl"]
