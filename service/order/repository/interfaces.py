"""Backed by `pkg.adapter.*`; the transaction adapter is dead wiring (constructed, never invoked). - **SQL-backed order repositories** — query, command, stats, stats-by-merchant and the stock-reservation ledger. - the shipping query port returns the raw proto `ShippingResponse` (holds the gRPC client directly), hence `Any`."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from pkg.database.schema.merchant import GetMerchantByIDRow
from pkg.database.schema.order import (
    GetMonthlyOrderRow,
    GetMonthlyTotalRevenueRow,
    GetOrderByIDRow,
    GetOrdersActiveRow,
    GetOrdersByMerchantRow,
    GetOrdersRow,
    GetOrdersTrashedRow,
    GetYearlyOrderRow,
    GetYearlyTotalRevenueRow,
    Order,
    OrderRow,
    OrderStockReservation,
)
from pkg.database.schema.order_item import (
    CreateOrderItemRow,
    GetOrderItemsByOrderRow,
    OrderItem,
    UpdateOrderItemRow,
)
from pkg.database.schema.product import AdjustProductStockRow, GetProductByIDRow
from pkg.database.schema.shipping_address import (
    CreateShippingAddressRow,
    UpdateShippingAddressRow,
)
from pkg.database.schema.user import GetUserByIDRow
from shared.domain.requests.order import (
    CreateOrderRecordRequest,
    FindAllOrder,
    FindAllOrderByMerchant,
    MonthOrderMerchant,
    MonthTotalRevenue,
    MonthTotalRevenueMerchant,
    UpdateOrderRecordRequest,
    YearOrderMerchant,
    YearTotalRevenueMerchant,
)
from shared.domain.requests.order_item import (
    CreateOrderItemRecordRequest,
    UpdateOrderItemRecordRequest,
)
from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    UpdateShippingAddressRequest,
)


class UserQueryRepository(Protocol):
    async def find_by_id(self, user_id: int) -> GetUserByIDRow: ...


class MerchantQueryRepository(Protocol):
    async def find_by_id(self, merchant_id: int) -> GetMerchantByIDRow: ...


class ProductQueryRepository(Protocol):
    async def find_by_id(self, product_id: int) -> GetProductByIDRow: ...


class ProductCommandRepository(Protocol):
    async def update_product_count_stock(
        self, product_id: int, stock: int
    ) -> AdjustProductStockRow: ...

    async def adjust_product_stock(
        self, product_id: int, delta: int, operation_id: str
    ) -> AdjustProductStockRow: ...


class OrderItemQueryRepository(Protocol):
    async def find_order_item_by_order(
        self, order_id: int
    ) -> list[GetOrderItemsByOrderRow]: ...

    async def calculate_total_price(self, order_id: int) -> int: ...


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

    async def delete_by_order_id_permanent(self, order_id: int) -> bool: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


class ShippingAddressCommandRepository(Protocol):
    async def create(
        self, request: CreateShippingAddressRequest
    ) -> CreateShippingAddressRow: ...

    async def update(
        self, request: UpdateShippingAddressRequest
    ) -> UpdateShippingAddressRow: ...

    async def delete_by_order_id_permanent(self, order_id: int) -> bool: ...

    async def delete_all(self) -> bool: ...


class ShippingQueryRepository(Protocol):
    async def find_by_id(self, shipping_id: int) -> Any: ...

    async def find_by_order(self, order_id: int) -> Any: ...


class TransactionCommandRepository(Protocol):
    async def delete_by_order_id_permanent(self, order_id: int) -> bool: ...

    async def delete_all(self) -> bool: ...


class OrderQueryRepository(Protocol):
    async def find_all(self, request: FindAllOrder) -> list[GetOrdersRow]: ...

    async def find_active(self, request: FindAllOrder) -> list[GetOrdersActiveRow]: ...

    async def find_trashed(self, request: FindAllOrder) -> list[GetOrdersTrashedRow]: ...

    async def find_by_merchant(
        self, request: FindAllOrderByMerchant
    ) -> list[GetOrdersByMerchantRow]: ...

    async def find_by_id(self, order_id: int) -> GetOrderByIDRow: ...


class OrderCommandRepository(Protocol):
    async def create(self, request: CreateOrderRecordRequest) -> OrderRow: ...

    async def update(self, request: UpdateOrderRecordRequest) -> OrderRow: ...

    async def trash(self, order_id: int) -> Order: ...

    async def restore(self, order_id: int) -> Order: ...

    async def delete_permanent(self, order_id: int) -> bool: ...

    async def delete_permanent_with_children(self, order_id: int) -> bool: ...

    async def find_trashed_by_id(self, order_id: int) -> Order: ...

    async def find_trashed(self) -> list[Order]: ...

    async def restore_all(self) -> bool: ...

    async def delete_all(self) -> bool: ...


class OrderStatsRepository(Protocol):
    async def get_monthly_total_revenue(
        self, request: MonthTotalRevenue
    ) -> list[GetMonthlyTotalRevenueRow]: ...

    async def get_yearly_total_revenue(
        self, year: int
    ) -> list[GetYearlyTotalRevenueRow]: ...

    async def get_monthly_order(self, year: int) -> list[GetMonthlyOrderRow]: ...

    async def get_yearly_order(self, year: int) -> list[GetYearlyOrderRow]: ...


class OrderStatsByMerchantRepository(Protocol):
    async def get_monthly_total_revenue_by_merchant(
        self, request: MonthTotalRevenueMerchant
    ) -> list[GetMonthlyTotalRevenueRow]: ...

    async def get_yearly_total_revenue_by_merchant(
        self, request: YearTotalRevenueMerchant
    ) -> list[GetYearlyTotalRevenueRow]: ...

    async def get_monthly_order_by_merchant(
        self, request: MonthOrderMerchant
    ) -> list[GetMonthlyOrderRow]: ...

    async def get_yearly_order_by_merchant(
        self, request: YearOrderMerchant
    ) -> list[GetYearlyOrderRow]: ...


class StockReservationRepository(Protocol):
    async def get_by_order(self, order_id: int) -> list[OrderStockReservation]: ...

    async def upsert(
        self, order_id: int, product_id: int, quantity: int
    ) -> OrderStockReservation: ...

    async def update_quantity(
        self, order_id: int, product_id: int, quantity: int
    ) -> OrderStockReservation: ...

    async def release(
        self, order_id: int, product_id: int
    ) -> OrderStockReservation: ...

    async def reserve(
        self, order_id: int, product_id: int
    ) -> OrderStockReservation: ...

    async def get_reserved_for_trashed_orders(
        self,
    ) -> list[OrderStockReservation]: ...

    async def get_released_for_trashed_orders(
        self,
    ) -> list[OrderStockReservation]: ...

    async def delete_by_order(self, order_id: int) -> None: ...

    async def delete_by_order_product(
        self, order_id: int, product_id: int
    ) -> None: ...

    async def delete_all_for_trashed_orders(self) -> None: ...

    async def get_released_for_active_orders(
        self,
    ) -> list[OrderStockReservation]: ...

    async def delete_old_released_reservations(self, cutoff: datetime) -> int: ...

    async def delete_old_product_stock_adjustments(self, cutoff: datetime) -> int: ...


__all__ = [
    "MerchantQueryRepository",
    "OrderCommandRepository",
    "OrderItemCommandRepository",
    "OrderItemQueryRepository",
    "OrderQueryRepository",
    "OrderStatsByMerchantRepository",
    "OrderStatsRepository",
    "ProductCommandRepository",
    "ProductQueryRepository",
    "ShippingAddressCommandRepository",
    "ShippingQueryRepository",
    "StockReservationRepository",
    "TransactionCommandRepository",
    "UserQueryRepository",
]
