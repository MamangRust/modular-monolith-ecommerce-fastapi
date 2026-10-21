"""Order item repository"""

from __future__ import annotations

from typing import Protocol

from pkg.database.schema.order_item import (
    CreateOrderItemRow,
    GetOrderItemsActiveRow,
    GetOrderItemsByOrderRow,
    GetOrderItemsRow,
    GetOrderItemsTrashedRow,
    OrderItem,
    UpdateOrderItemRow,
)
from shared.domain.requests.order_item import (
    CreateOrderItemRecordRequest,
    UpdateOrderItemRecordRequest,
)


class OrderItemQueryRepository(Protocol):
    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> list[GetOrderItemsRow]: ...

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> list[GetOrderItemsActiveRow]: ...

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> list[GetOrderItemsTrashedRow]: ...

    async def find_order_item_by_order(
        self, order_id: int
    ) -> list[GetOrderItemsByOrderRow]: ...


class OrderItemCommandRepository(Protocol):
    async def create(
        self, request: CreateOrderItemRecordRequest
    ) -> CreateOrderItemRow: ...

    async def update(
        self, request: UpdateOrderItemRecordRequest
    ) -> UpdateOrderItemRow: ...

    async def trash(self, order_item_id: int) -> OrderItem: ...

    async def restore(self, order_item_id: int) -> OrderItem: ...

    async def delete_permanent(self, order_item_id: int) -> bool: ...

    async def delete_order_item_by_order_permanent(self, order_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...

    async def calculate_total_price(self, order_id: int) -> int: ...


__all__ = ["OrderItemCommandRepository", "OrderItemQueryRepository"]
