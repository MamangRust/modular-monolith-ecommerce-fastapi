"""Unit tests for the order services (no DB/Redis). Covers the cache-first query/stats services and the command saga: - `create` runs the multi-service saga (reserve stock -> reservation ledger -> order item -> shipping -> total -> finalise) and unwinds on failure; - `create` maps a lost stock race to `err_insufficient_product_stock`; - `update` validation guards (`order id is required`, `quantity must be greater than zero`, `does not belong to order`, `changing. Every fake records into a shared `calls` list so the saga's ordering can be asserted. Errors from repositories/adapters propagate unchanged (`HandleError`)."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest

from pkg.database.errors import NoRowsError
from pkg.database.schema.order import Order, OrderRow, OrderStockReservation
from pkg.database.schema.order_item import (
    CreateOrderItemRow,
    GetOrderItemsByOrderRow,
)
from pkg.database.schema.product import GetProductByIDRow
from pkg.database.schema.shipping_address import CreateShippingAddressRow
from pkg.logger.logger import Logger
from service.order.service.order_command_service import OrderCommandServiceImpl
from service.order.service.order_query_service import OrderQueryServiceImpl
from service.order.service.order_stats_by_merchant_service import (
    OrderStatsByMerchantServiceImpl,
)
from service.order.service.order_stats_service import OrderStatsServiceImpl
from shared.domain.requests.order import (
    CreateOrderItemRequest,
    CreateOrderRequest,
    FindAllOrder,
    MonthTotalRevenue,
    MonthTotalRevenueMerchant,
    UpdateOrderItemRequest,
    UpdateOrderRequest,
)
from shared.domain.requests.shipping_address import CreateShippingAddressRequest
from shared.errors import AppError
from shared.errors.order_errors import err_insufficient_product_stock
from shared.observability import Observability

CREATED = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
UPDATED = datetime(2026, 1, 3, 4, 5, 6, tzinfo=UTC)


def _logger() -> Logger:
    return Logger("test", "error")


def _obs() -> Observability:
    return Observability("test", _logger())


def _product_row(**overrides: Any) -> GetProductByIDRow:
    base = GetProductByIDRow(
        product_id=10,
        merchant_id=3,
        category_id=2,
        name="Galaxy S24",
        description="d",
        price=5000,
        count_in_stock=100,
        brand="Samsung",
        weight=200,
        rating=4.5,
        slug_product="galaxy-s24",
        image_product="galaxy-s24.jpg",
        created_at=CREATED,
        updated_at=UPDATED,
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


def _order_row(order_id: int = 42, total_price: int = 0) -> OrderRow:
    return OrderRow(
        order_id=order_id,
        user_id=7,
        merchant_id=3,
        total_price=total_price,
        created_at=CREATED,
        updated_at=UPDATED,
    )


def _reservation(
    order_id: int = 42,
    product_id: int = 10,
    quantity: int = 2,
    status: str = "reserved",
) -> OrderStockReservation:
    return OrderStockReservation(
        reservation_id=1,
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        status=status,
        created_at=CREATED,
        updated_at=UPDATED,
    )


def _order_item(
    order_item_id: int = 5,
    order_id: int = 42,
    product_id: int = 10,
    quantity: int = 2,
    price: int = 5000,
) -> GetOrderItemsByOrderRow:
    return GetOrderItemsByOrderRow(
        order_item_id=order_item_id,
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        price=price,
        created_at=CREATED,
        updated_at=UPDATED,
    )


def _shipping(order_id: int = 42, cost: int = 1500) -> SimpleNamespace:
    return SimpleNamespace(
        id=9,
        order_id=order_id,
        alamat="Jalan Panjang",
        provinsi="DKI",
        kota="Jakarta",
        courier="jne",
        shippingMethod="reg",
        shippingCost=cost,
        negara="Indonesia",
    )


# --------------------------------------------------------------------- fakes


class FakeOrderQuery:
    def __init__(self, calls, rows=None, row=None, error=None):
        self._calls = calls
        self._rows = rows or []
        self._row = row
        self._error = error

    async def find_all(self, request):
        self._calls.append("order.find_all")
        if self._error:
            raise self._error
        return self._rows

    async def find_active(self, request):
        self._calls.append("order.find_active")
        if self._error:
            raise self._error
        return self._rows

    async def find_trashed(self, request):
        self._calls.append("order.find_trashed")
        if self._error:
            raise self._error
        return self._rows

    async def find_by_merchant(self, request):
        self._calls.append("order.find_by_merchant")
        if self._error:
            raise self._error
        return self._rows

    async def find_by_id(self, order_id):
        self._calls.append(f"order.find_by_id:{order_id}")
        if self._error:
            raise self._error
        return self._row if self._row is not None else _order_row(order_id)


class FakeOrderCommand:
    def __init__(self, calls, *, trashed=None):
        self._calls = calls
        self._trashed = trashed or []

    async def create(self, request):
        self._calls.append(f"order.create:{request.user_id}")
        return _order_row(42)

    async def update(self, request):
        self._calls.append(f"order.update:{request.order_id}:{request.total_price}")
        return _order_row(request.order_id, request.total_price)

    async def trash(self, order_id):
        self._calls.append(f"order.trash:{order_id}")
        return Order(
            order_id=order_id,
            user_id=7,
            merchant_id=3,
            total_price=0,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=UPDATED,
        )

    async def restore(self, order_id):
        self._calls.append(f"order.restore:{order_id}")
        return Order(
            order_id=order_id,
            user_id=7,
            merchant_id=3,
            total_price=0,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, order_id):
        self._calls.append(f"order.delete_permanent:{order_id}")
        return True

    async def delete_permanent_with_children(self, order_id):
        self._calls.append(f"order.delete_permanent_with_children:{order_id}")
        return True

    async def find_trashed(self):
        self._calls.append("order.find_trashed_rows")
        return self._trashed


class FakeProductQuery:
    def __init__(self, calls, *, row=None, error=None):
        self._calls = calls
        self._row = row if row is not None else _product_row()
        self._error = error

    async def find_by_id(self, product_id):
        self._calls.append(f"product.find:{product_id}")
        if self._error:
            raise self._error
        return self._row


class FakeProductCommand:
    def __init__(self, calls, *, error=None):
        self._calls = calls
        self._error = error

    async def adjust_product_stock(self, product_id, delta, operation_id):
        self._calls.append(f"product.adjust:{product_id}:{delta}")
        if self._error:
            raise self._error
        return SimpleNamespace(product_id=product_id, count_in_stock=100)


class FakeOrderItemQuery:
    def __init__(self, calls, *, items=None, total=0, error=None):
        self._calls = calls
        self._items = items or []
        self._total = total
        self._error = error

    async def find_order_item_by_order(self, order_id):
        self._calls.append(f"order_item.find_by_order:{order_id}")
        if self._error:
            raise self._error
        return self._items

    async def calculate_total_price(self, order_id):
        self._calls.append(f"order_item.total:{order_id}")
        return self._total


class FakeOrderItemCommand:
    def __init__(self, calls, *, error=None):
        self._calls = calls
        self._error = error

    async def create(self, request):
        self._calls.append(
            f"order_item.create:{request.order_id}:{request.product_id}:"
            f"{request.quantity}:{request.price}"
        )
        if self._error:
            raise self._error
        return CreateOrderItemRow(
            order_item_id=5,
            order_id=request.order_id,
            product_id=request.product_id,
            quantity=request.quantity,
            price=request.price,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self._calls.append(f"order_item.update:{request.order_item_id}")
        if self._error:
            raise self._error
        return CreateOrderItemRow(
            order_item_id=request.order_item_id,
            order_id=request.order_id,
            product_id=request.product_id,
            quantity=request.quantity,
            price=request.price,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, order_item_id):
        self._calls.append(f"order_item.trash:{order_item_id}")
        return _order_item(order_item_id=order_item_id)

    async def delete_permanent(self, order_item_id):
        self._calls.append(f"order_item.delete_permanent:{order_item_id}")
        return True


class FakeShippingCommand:
    def __init__(self, calls, *, error=None):
        self._calls = calls
        self._error = error

    async def create(self, request):
        self._calls.append(f"shipping.create:{request.order_id}")
        if self._error:
            raise self._error
        return CreateShippingAddressRow(
            shipping_address_id=9,
            order_id=request.order_id,
            alamat=request.alamat,
            provinsi=request.provinsi,
            negara=request.negara,
            kota=request.kota,
            courier=request.courier,
            shipping_method=request.shipping_method,
            shipping_cost=float(request.shipping_cost),
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self._calls.append(f"shipping.update:{request.shipping_id}")
        if self._error:
            raise self._error
        return CreateShippingAddressRow(
            shipping_address_id=request.shipping_id or 9,
            order_id=request.order_id,
            alamat=request.alamat,
            provinsi=request.provinsi,
            negara=request.negara,
            kota=request.kota,
            courier=request.courier,
            shipping_method=request.shipping_method,
            shipping_cost=float(request.shipping_cost),
            created_at=CREATED,
            updated_at=UPDATED,
        )


class FakeShippingQuery:
    def __init__(self, calls, *, by_order=None, by_id=None, error=None):
        self._calls = calls
        self._by_order = by_order
        self._by_id = by_id
        self._error = error

    async def find_by_id(self, shipping_id):
        self._calls.append(f"shipping.find_by_id:{shipping_id}")
        if self._error:
            raise self._error
        return self._by_id

    async def find_by_order(self, order_id):
        self._calls.append(f"shipping.find_by_order:{order_id}")
        if self._error:
            raise self._error
        return self._by_order


class FakeStock:
    def __init__(self, calls, *, by_order=None, released_active=None, reserved_trashed=None):
        self._calls = calls
        self._by_order = by_order or []
        self._released_active = released_active or []
        self._reserved_trashed = reserved_trashed or []
        self._error_release = None
        self._error_reserve = None

    async def upsert(self, order_id, product_id, quantity):
        self._calls.append(f"stock.upsert:{order_id}:{product_id}:{quantity}")
        return _reservation(order_id, product_id, quantity)

    async def update_quantity(self, order_id, product_id, quantity):
        self._calls.append(f"stock.update_quantity:{order_id}:{product_id}:{quantity}")
        return _reservation(order_id, product_id, quantity)

    async def release(self, order_id, product_id):
        self._calls.append(f"stock.release:{order_id}:{product_id}")
        if self._error_release:
            raise self._error_release
        return _reservation(order_id, product_id, status="released")

    async def reserve(self, order_id, product_id):
        self._calls.append(f"stock.reserve:{order_id}:{product_id}")
        if self._error_reserve:
            raise self._error_reserve
        return _reservation(order_id, product_id, status="reserved")

    async def get_by_order(self, order_id):
        self._calls.append(f"stock.get_by_order:{order_id}")
        return self._by_order

    async def get_reserved_for_trashed_orders(self):
        self._calls.append("stock.reserved_trashed")
        return self._reserved_trashed

    async def get_released_for_active_orders(self):
        self._calls.append("stock.released_active")
        return self._released_active

    async def delete_by_order_product(self, order_id, product_id):
        self._calls.append(f"stock.delete:{order_id}:{product_id}")

    async def delete_old_released_reservations(self, cutoff):
        self._calls.append("stock.delete_old_released")
        return 2

    async def delete_old_product_stock_adjustments(self, cutoff):
        self._calls.append("stock.delete_old_adjustments")
        return 3


class FakeCommandCache:
    def __init__(self, calls):
        self._calls = calls

    async def delete_order_cache(self, order_id):
        self._calls.append(f"cache.delete:{order_id}")
        return 1

    async def invalidate_order_cache(self):
        self._calls.append("cache.invalidate")
        return 1


def _command_service(calls, **overrides):
    fakes = {
        "user_query": SimpleNamespace(),
        "merchant_query": SimpleNamespace(),
        "product_query": FakeProductQuery(calls),
        "product_command": FakeProductCommand(calls),
        "order_query": FakeOrderQuery(calls),
        "order_command": FakeOrderCommand(calls),
        "order_item_query": FakeOrderItemQuery(calls),
        "order_item_command": FakeOrderItemCommand(calls),
        "shipping_address": FakeShippingCommand(calls),
        "transaction_command": SimpleNamespace(),
        "shipping_query": FakeShippingQuery(calls, by_order=_shipping()),
        "stock_reservation": FakeStock(calls),
        "cache": FakeCommandCache(calls),
    }
    fakes.update(overrides)
    return OrderCommandServiceImpl(logger=_logger(), obs=_obs(), **fakes)


def _create_request(**overrides: Any) -> CreateOrderRequest:
    base = {
        "merchant_id": 3,
        "user_id": 7,
        "total_price": 1,
        "items": [CreateOrderItemRequest(product_id=10, quantity=2, price=5000)],
        "shipping_address": CreateShippingAddressRequest(
            alamat="Jalan Panjang",
            provinsi="DKI",
            kota="Jakarta",
            courier="jne",
            shipping_method="reg",
            shipping_cost=1500,
            negara="Indonesia",
        ),
    }
    base.update(overrides)
    return CreateOrderRequest(**base)


# ------------------------------------------------------------- query service


class FakeQueryRepo:
    def __init__(self, rows=None):
        self._rows = rows or []
        self.calls: list[str] = []

    async def find_all(self, request):
        self.calls.append("find_all")
        return self._rows

    async def find_active(self, request):
        self.calls.append("find_active")
        return self._rows

    async def find_trashed(self, request):
        self.calls.append("find_trashed")
        return self._rows

    async def find_by_merchant(self, request):
        self.calls.append("find_by_merchant")
        return self._rows

    async def find_by_id(self, order_id):
        self.calls.append("find_by_id")
        return self._rows[0]


class FakeQueryCache:
    def __init__(self):
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_all(self, request):
        return self.store.get("all")

    async def set_all(self, request, rows, total):
        self.writes.append("all")
        self.store["all"] = (rows, total)

    async def get_active(self, request):
        return self.store.get("active")

    async def set_active(self, request, rows, total):
        self.writes.append("active")
        self.store["active"] = (rows, total)

    async def get_trashed(self, request):
        return self.store.get("trashed")

    async def set_trashed(self, request, rows, total):
        self.writes.append("trashed")
        self.store["trashed"] = (rows, total)

    async def get_by_merchant(self, request):
        return self.store.get("by_merchant")

    async def set_by_merchant(self, request, rows, total):
        self.writes.append("by_merchant")
        self.store["by_merchant"] = (rows, total)

    async def get_by_id(self, order_id):
        return self.store.get("by_id")

    async def set_by_id(self, row):
        self.writes.append("by_id")
        self.store["by_id"] = row


def _query_service(repo, cache):
    return OrderQueryServiceImpl(repo, cache, _logger(), _obs())


async def test_query_find_all_caches_and_serves_cache_first() -> None:
    from pkg.database.schema.order import GetOrdersRow

    row = GetOrdersRow(
        order_id=42,
        user_id=7,
        merchant_id=3,
        total_price=100,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=11,
    )
    repo, cache = FakeQueryRepo([row]), FakeQueryCache()
    service = _query_service(repo, cache)

    rows, total = await service.find_all(
        FindAllOrder(search="", page=1, page_size=10)
    )
    assert total == 11
    assert cache.writes == ["all"]
    repo.calls.clear()

    cached, _ = await service.find_all(FindAllOrder(search="", page=1, page_size=10))
    assert repo.calls == []
    assert cached[0].order_id == 42


async def test_query_empty_page_reports_zero_total() -> None:
    rows, total = await _query_service(FakeQueryRepo([]), FakeQueryCache()).find_all(
        FindAllOrder(search="", page=1, page_size=10)
    )
    assert rows == []
    assert total == 0


async def test_query_find_by_id_caches() -> None:
    from pkg.database.schema.order import GetOrderByIDRow

    row = GetOrderByIDRow(
        order_id=42,
        user_id=7,
        merchant_id=3,
        total_price=100,
        created_at=CREATED,
        updated_at=UPDATED,
    )
    repo, cache = FakeQueryRepo([row]), FakeQueryCache()
    service = _query_service(repo, cache)

    result = await service.find_by_id(42)
    assert result.order_id == 42
    assert cache.writes == ["by_id"]
    repo.calls.clear()

    await service.find_by_id(42)
    assert repo.calls == []


async def test_query_errors_propagate_unchanged() -> None:
    class FailingRepo(FakeQueryRepo):
        async def find_all(self, request):
            raise AppError("INTERNAL", 500, "boom")

    with pytest.raises(AppError) as excinfo:
        await _query_service(FailingRepo(), FakeQueryCache()).find_all(
            FindAllOrder(search="", page=1, page_size=10)
        )
    assert excinfo.value.code == 500
    assert excinfo.value.message == "boom"


# ------------------------------------------------------------- stats service


class FakeStatsRepo:
    def __init__(self):
        self.calls: list[str] = []

    async def get_monthly_total_revenue(self, request):
        self.calls.append("monthly_total")
        return ["m"]

    async def get_yearly_total_revenue(self, year):
        self.calls.append("yearly_total")
        return ["y"]

    async def get_monthly_order(self, year):
        self.calls.append("monthly_order")
        return ["mo"]

    async def get_yearly_order(self, year):
        self.calls.append("yearly_order")
        return ["yo"]


class FakeStatsCache:
    def __init__(self):
        self.store: dict[str, Any] = {}

    async def get_monthly_total_revenue(self, request):
        return self.store.get("mt")

    async def set_monthly_total_revenue(self, request, rows):
        self.store["mt"] = rows

    async def get_yearly_total_revenue(self, year):
        return self.store.get("yt")

    async def set_yearly_total_revenue(self, year, rows):
        self.store["yt"] = rows

    async def get_monthly_order(self, year):
        return self.store.get("mo")

    async def set_monthly_order(self, year, rows):
        self.store["mo"] = rows

    async def get_yearly_order(self, year):
        return self.store.get("yo")

    async def set_yearly_order(self, year, rows):
        self.store["yo"] = rows


async def test_stats_service_is_cache_first() -> None:
    repo, cache = FakeStatsRepo(), FakeStatsCache()
    service = OrderStatsServiceImpl(repo, cache, _logger(), _obs())

    first = await service.find_monthly_total_revenue(
        MonthTotalRevenue(year=2001, month=3)
    )
    assert first == ["m"]
    assert repo.calls == ["monthly_total"]
    repo.calls.clear()

    cached = await service.find_monthly_total_revenue(
        MonthTotalRevenue(year=2001, month=3)
    )
    assert cached == ["m"]
    assert repo.calls == []


class FakeStatsByMerchantRepo:
    def __init__(self):
        self.calls: list[str] = []

    async def get_monthly_total_revenue_by_merchant(self, request):
        self.calls.append("m")
        return ["bm"]

    async def get_yearly_total_revenue_by_merchant(self, request):
        self.calls.append("y")
        return ["by"]

    async def get_monthly_order_by_merchant(self, request):
        self.calls.append("mo")
        return ["bmo"]

    async def get_yearly_order_by_merchant(self, request):
        self.calls.append("yo")
        return ["byo"]


class FakeStatsByMerchantCache:
    def __init__(self):
        self.store: dict[str, Any] = {}

    async def get_monthly_total_revenue_by_merchant(self, request):
        return self.store.get("m")

    async def set_monthly_total_revenue_by_merchant(self, request, rows):
        self.store["m"] = rows

    async def get_yearly_total_revenue_by_merchant(self, request):
        return None

    async def set_yearly_total_revenue_by_merchant(self, request, rows):
        self.store["y"] = rows

    async def get_monthly_order_by_merchant(self, request):
        return None

    async def set_monthly_order_by_merchant(self, request, rows):
        self.store["mo"] = rows

    async def get_yearly_order_by_merchant(self, request):
        return None

    async def set_yearly_order_by_merchant(self, request, rows):
        self.store["yo"] = rows


async def test_stats_by_merchant_service_is_cache_first() -> None:
    repo, cache = FakeStatsByMerchantRepo(), FakeStatsByMerchantCache()
    service = OrderStatsByMerchantServiceImpl(repo, cache, _logger(), _obs())

    first = await service.find_monthly_total_revenue_by_merchant(
        MonthTotalRevenueMerchant(merchant_id=3, year=2001, month=3)
    )
    assert first == ["bm"]
    repo.calls.clear()

    cached = await service.find_monthly_total_revenue_by_merchant(
        MonthTotalRevenueMerchant(merchant_id=3, year=2001, month=3)
    )
    assert cached == ["bm"]
    assert repo.calls == []


# ----------------------------------------------------------- command service


async def test_create_runs_full_saga() -> None:
    calls: list[str] = []
    service = _command_service(
        calls,
        order_item_query=FakeOrderItemQuery(calls, total=10000),
    )

    row = await service.create(_create_request())

    assert row.order_id == 42
    # 10000 items + 1500 shipping.
    assert row.total_price == 11500
    assert calls == [
        "order.create:7",
        "product.find:10",
        "product.adjust:10:-2",
        "stock.upsert:42:10:2",
        "order_item.create:42:10:2:5000",
        "shipping.create:42",
        "order_item.total:42",
        "order.update:42:11500",
    ]


async def test_create_insufficient_stock_rolls_back() -> None:
    calls: list[str] = []
    # Product claims stock 1 while the saga tries to reserve 2; the adjust RPC
    # loses the guarded UPDATE.
    service = _command_service(
        calls,
        product_query=FakeProductQuery(calls, row=_product_row(count_in_stock=1)),
        product_command=FakeProductCommand(calls, error=AppError("BAD", 400, "stock")),
    )

    with pytest.raises(AppError) as excinfo:
        await service.create(_create_request())
    assert excinfo.value is err_insufficient_product_stock

    # No reservation was recorded, so the rollback only trashes + purges the
    # half-created order.
    assert "order.trash:42" in calls
    assert "order.delete_permanent_with_children:42" in calls
    assert not any(call.startswith("stock.upsert") for call in calls)


async def test_create_shipping_failure_rolls_back_reserved_stock() -> None:
    calls: list[str] = []
    service = _command_service(
        calls,
        shipping_address=FakeShippingCommand(calls, error=AppError("BAD", 500, "ship")),
    )

    with pytest.raises(AppError):
        await service.create(_create_request())

    # The reserved stock is released and adjusted back before the order purge.
    assert "stock.release:42:10" in calls
    assert "product.adjust:10:2" in calls
    assert "order.trash:42" in calls
    assert "order.delete_permanent_with_children:42" in calls


async def test_update_requires_order_id() -> None:
    calls: list[str] = []
    service = _command_service(calls)
    request = UpdateOrderRequest(
        order_id=None,
        user_id=7,
        total_price=1,
        items=[UpdateOrderItemRequest(order_item_id=5, product_id=10, quantity=2)],
    )
    with pytest.raises(AppError) as excinfo:
        await service.update(request)
    assert excinfo.value.message == "order id is required"


async def test_update_quantity_must_be_positive() -> None:
    calls: list[str] = []
    service = _command_service(
        calls,
        order_item_query=FakeOrderItemQuery(calls, items=[_order_item()]),
    )
    request = UpdateOrderRequest(
        order_id=42,
        user_id=7,
        total_price=1,
        items=[UpdateOrderItemRequest(order_item_id=5, product_id=10, quantity=0)],
    )
    with pytest.raises(AppError) as excinfo:
        await service.update(request)
    assert excinfo.value.message == "order item quantity must be greater than zero"


async def test_update_item_must_belong_to_order() -> None:
    calls: list[str] = []
    service = _command_service(
        calls,
        order_item_query=FakeOrderItemQuery(calls, items=[_order_item()]),
    )
    request = UpdateOrderRequest(
        order_id=42,
        user_id=7,
        total_price=1,
        items=[UpdateOrderItemRequest(order_item_id=99, product_id=10, quantity=2)],
    )
    with pytest.raises(AppError) as excinfo:
        await service.update(request)
    assert excinfo.value.message == "order item does not belong to order"


async def test_update_cannot_change_item_product() -> None:
    calls: list[str] = []
    service = _command_service(
        calls,
        order_item_query=FakeOrderItemQuery(calls, items=[_order_item()]),
    )
    request = UpdateOrderRequest(
        order_id=42,
        user_id=7,
        total_price=1,
        items=[UpdateOrderItemRequest(order_item_id=5, product_id=999, quantity=2)],
    )
    with pytest.raises(AppError) as excinfo:
        await service.update(request)
    assert excinfo.value.message == "changing an order item's product is not supported"


async def test_update_success_moves_stock_and_recomputes_total() -> None:
    calls: list[str] = []
    service = _command_service(
        calls,
        order_item_query=FakeOrderItemQuery(calls, items=[_order_item()], total=15000),
        stock_reservation=FakeStock(calls, by_order=[_reservation()]),
        shipping_query=FakeShippingQuery(calls, by_order=_shipping(cost=1500)),
    )
    request = UpdateOrderRequest(
        order_id=42,
        user_id=7,
        total_price=1,
        items=[UpdateOrderItemRequest(order_item_id=5, product_id=10, quantity=3)],
    )

    row = await service.update(request)

    # delta = 2 - 3 = -1 -> reserve one more unit.
    assert "product.adjust:10:-1" in calls
    assert "stock.update_quantity:42:10:3" in calls
    assert "order_item.update:5" in calls
    assert "shipping.find_by_order:42" in calls
    # 15000 items + 1500 (previous shipping, unchanged) and the cache is dropped.
    assert row.total_price == 16500
    assert "cache.delete:42" in calls


async def test_update_uses_supplied_shipping_id() -> None:
    from shared.domain.requests.shipping_address import UpdateShippingAddressRequest

    calls: list[str] = []
    service = _command_service(
        calls,
        order_item_query=FakeOrderItemQuery(calls, items=[_order_item()], total=15000),
        stock_reservation=FakeStock(calls, by_order=[_reservation()]),
        shipping_query=FakeShippingQuery(calls, by_id=_shipping(cost=2000)),
    )
    request = UpdateOrderRequest(
        order_id=42,
        user_id=7,
        total_price=1,
        items=[UpdateOrderItemRequest(order_item_id=5, product_id=10, quantity=2)],
        shipping_address=UpdateShippingAddressRequest(
            shipping_id=9,
            alamat="New Address",
            provinsi="DKI",
            kota="Jakarta",
            courier="jne",
            shipping_method="reg",
            shipping_cost=2000,
            negara="Indonesia",
        ),
    )

    row = await service.update(request)

    assert "shipping.find_by_id:9" in calls
    assert "shipping.update:9" in calls
    assert row.total_price == 17000  # 15000 + 2000


async def test_trash_releases_reservations_and_evicts() -> None:
    calls: list[str] = []
    service = _command_service(
        calls, stock_reservation=FakeStock(calls, by_order=[_reservation()])
    )

    order = await service.trash(42)

    assert order.deleted_at is not None
    assert "stock.release:42:10" in calls
    assert "product.adjust:10:2" in calls
    assert "order.trash:42" in calls
    assert "cache.delete:42" in calls


async def test_trash_skips_already_claimed_reservation() -> None:
    calls: list[str] = []
    stock = FakeStock(calls, by_order=[_reservation()])
    stock._error_release = NoRowsError()
    service = _command_service(calls, stock_reservation=stock)

    await service.trash(42)

    # A NoRowsError means another worker claimed the transition; the order is
    # still trashed without a stock adjustment.
    assert "order.trash:42" in calls
    assert not any(call.startswith("product.adjust") for call in calls)


async def test_restore_re_reserves_and_evicts() -> None:
    calls: list[str] = []
    service = _command_service(
        calls, stock_reservation=FakeStock(calls, by_order=[_reservation(status="released")])
    )

    order = await service.restore(42)

    assert order.deleted_at is None
    assert "stock.reserve:42:10" in calls
    assert "product.adjust:10:-2" in calls
    assert "order.restore:42" in calls
    assert "cache.delete:42" in calls


async def test_delete_permanent_purges_children_and_evicts() -> None:
    calls: list[str] = []
    service = _command_service(calls)

    assert await service.delete_permanent(42) is True
    assert "order.delete_permanent_with_children:42" in calls
    assert "cache.delete:42" in calls


async def test_restore_all_and_delete_all() -> None:
    calls: list[str] = []
    trashed = [
        Order(1, 7, 3, 0, CREATED, UPDATED, UPDATED),
        Order(2, 7, 3, 0, CREATED, UPDATED, UPDATED),
    ]
    service = _command_service(
        calls, order_command=FakeOrderCommand(calls, trashed=trashed)
    )

    assert await service.restore_all() is True
    assert "order.restore:1" in calls
    assert "order.restore:2" in calls
    assert "cache.invalidate" in calls

    assert await service.delete_all() is True
    assert "order.delete_permanent_with_children:1" in calls
    assert "order.delete_permanent_with_children:2" in calls


async def test_reconcile_stock_reservations_repairs_both_directions() -> None:
    calls: list[str] = []
    stock = FakeStock(
        calls,
        released_active=[_reservation(order_id=1, product_id=10, quantity=2, status="released")],
        reserved_trashed=[_reservation(order_id=2, product_id=11, quantity=3, status="reserved")],
    )
    service = _command_service(calls, stock_reservation=stock)

    result = await service.reconcile_stock_reservations()

    assert result.re_reserved == 1
    assert result.released == 1
    assert "stock.reserve:1:10" in calls
    assert "product.adjust:10:-2" in calls
    assert "stock.release:2:11" in calls
    assert "product.adjust:11:3" in calls


async def test_cleanup_idempotency_records_defaults_retention() -> None:
    calls: list[str] = []
    service = _command_service(calls)

    result = await service.cleanup_idempotency_records(0)

    assert result.released_reservations_removed == 2
    assert result.adjustments_removed == 3
    assert "stock.delete_old_released" in calls
    assert "stock.delete_old_adjustments" in calls


__all__ = []
