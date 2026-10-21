"""Order item cache"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.order_item import (
    GetOrderItemsActiveRow,
    GetOrderItemsByOrderRow,
    GetOrderItemsRow,
    GetOrderItemsTrashedRow,
)


class OrderItemQueryCache(Protocol):
    async def get_order_items_all(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetOrderItemsRow], int] | None: ...

    async def set_order_items_all(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetOrderItemsRow],
        total: int,
    ) -> None: ...

    async def get_order_item_active(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetOrderItemsActiveRow], int] | None: ...

    async def set_order_item_active(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetOrderItemsActiveRow],
        total: int,
    ) -> None: ...

    async def get_order_item_trashed(
        self, page: int, page_size: int, search: str
    ) -> tuple[list[GetOrderItemsTrashedRow], int] | None: ...

    async def set_order_item_trashed(
        self,
        page: int,
        page_size: int,
        search: str,
        rows: list[GetOrderItemsTrashedRow],
        total: int,
    ) -> None: ...

    async def get_order_items(
        self, order_id: int
    ) -> list[GetOrderItemsByOrderRow] | None: ...

    async def set_order_items(self, rows: list[GetOrderItemsByOrderRow]) -> None: ...


class OrderItemCommandCache(Protocol):
    async def invalidate_order_item_cache(self) -> int: ...


__all__ = ["OrderItemCommandCache", "OrderItemQueryCache"]
