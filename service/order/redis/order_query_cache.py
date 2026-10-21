"""order query cache.

Reads/writes never raise: `CacheStore` swallows Redis errors so a cache outage
degrades to a DB read. Each list page stores `{data, total_records}`; the by-id
entry stores the row directly."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pkg.database.schema.order import (
    GetOrdersActiveRow,
    GetOrdersByMerchantRow,
    GetOrdersRow,
    GetOrdersTrashedRow,
    OrderRow,
)
from pkg.logger.logger import Logger
from service.order.redis.cache import (
    order_by_id_from_dict,
    order_by_id_to_dict,
    orders_active_row_from_dict,
    orders_active_row_to_dict,
    orders_row_from_dict,
    orders_row_to_dict,
    orders_trashed_row_from_dict,
    orders_trashed_row_to_dict,
)
from service.order.redis.common import (
    TTL_DEFAULT,
    order_active_key,
    order_all_key,
    order_by_id_key,
    order_by_merchant_key,
    order_trashed_key,
)
from shared.cache import CacheStore
from shared.domain.requests.order import FindAllOrder, FindAllOrderByMerchant


def _encode[T](
    rows: list[T], total: int, to_dict: Callable[[T], dict[str, Any]]
) -> dict[str, Any]:
    return {"data": [to_dict(row) for row in rows], "total_records": total}


def _decode[T](
    payload: Any, from_dict: Callable[[dict[str, Any], int], T]
) -> tuple[list[T], int] | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, list):
        return None
    total = int(payload.get("total_records") or 0)
    return [from_dict(item, total) for item in data], total


class OrderQueryCacheImpl:
    def __init__(self, store: CacheStore, logger: Logger) -> None:
        self._store = store
        self._logger = logger

    # ---- FindAll ----

    async def get_all(
        self, request: FindAllOrder
    ) -> tuple[list[GetOrdersRow], int] | None:
        payload = await self._store.get_json(
            order_all_key(request.page, request.page_size, request.search)
        )
        return _decode(payload, orders_row_from_dict)

    async def set_all(
        self, request: FindAllOrder, rows: list[GetOrdersRow], total: int
    ) -> None:
        await self._store.set_json(
            order_all_key(request.page, request.page_size, request.search),
            _encode(rows, total, orders_row_to_dict),
            TTL_DEFAULT,
        )

    # ---- FindActive ----

    async def get_active(
        self, request: FindAllOrder
    ) -> tuple[list[GetOrdersActiveRow], int] | None:
        payload = await self._store.get_json(
            order_active_key(request.page, request.page_size, request.search)
        )
        return _decode(payload, orders_active_row_from_dict)

    async def set_active(
        self, request: FindAllOrder, rows: list[GetOrdersActiveRow], total: int
    ) -> None:
        await self._store.set_json(
            order_active_key(request.page, request.page_size, request.search),
            _encode(rows, total, orders_active_row_to_dict),
            TTL_DEFAULT,
        )

    # ---- FindTrashed ----

    async def get_trashed(
        self, request: FindAllOrder
    ) -> tuple[list[GetOrdersTrashedRow], int] | None:
        payload = await self._store.get_json(
            order_trashed_key(request.page, request.page_size, request.search)
        )
        return _decode(payload, orders_trashed_row_from_dict)

    async def set_trashed(
        self, request: FindAllOrder, rows: list[GetOrdersTrashedRow], total: int
    ) -> None:
        await self._store.set_json(
            order_trashed_key(request.page, request.page_size, request.search),
            _encode(rows, total, orders_trashed_row_to_dict),
            TTL_DEFAULT,
        )

    # ---- FindByMerchant ----

    async def get_by_merchant(
        self, request: FindAllOrderByMerchant
    ) -> tuple[list[GetOrdersByMerchantRow], int] | None:
        payload = await self._store.get_json(
            order_by_merchant_key(
                request.merchant_id, request.page, request.page_size, request.search
            )
        )
        return _decode(payload, orders_row_from_dict)

    async def set_by_merchant(
        self,
        request: FindAllOrderByMerchant,
        rows: list[GetOrdersByMerchantRow],
        total: int,
    ) -> None:
        await self._store.set_json(
            order_by_merchant_key(
                request.merchant_id, request.page, request.page_size, request.search
            ),
            _encode(rows, total, orders_row_to_dict),
            TTL_DEFAULT,
        )

    # ---- FindByID ----

    async def get_by_id(self, order_id: int) -> OrderRow | None:
        payload = await self._store.get_json(order_by_id_key(order_id))
        return order_by_id_from_dict(payload)

    async def set_by_id(self, row: OrderRow) -> None:
        await self._store.set_json(
            order_by_id_key(row.order_id),
            order_by_id_to_dict(row),
            TTL_DEFAULT,
        )


__all__ = ["OrderQueryCacheImpl"]
