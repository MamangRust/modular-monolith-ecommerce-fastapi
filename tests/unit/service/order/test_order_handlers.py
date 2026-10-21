"""Unit tests for the order gRPC handlers (no DB/Redis)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest

from pb.order import order_command_pb2, order_common_pb2, order_query_pb2
from pb.order.stats import order_stats_pb2, order_statsbymerchant_pb2
from pb.shipping_address import shipping_address_command_pb2
from pkg.database.schema.order import (
    GetMonthlyOrderRow,
    GetMonthlyTotalRevenueRow,
    GetOrdersActiveRow,
    GetOrdersRow,
    GetOrdersTrashedRow,
    GetYearlyOrderRow,
    GetYearlyTotalRevenueRow,
    OrderRow,
)
from pkg.logger.logger import Logger
from service.order.handler.order_command import OrderCommandHandler
from service.order.handler.order_query import OrderQueryHandler
from service.order.handler.order_stats import OrderStatsHandler
from shared.errors.order_errors import (
    err_grpc_order_invalid_id,
    err_grpc_order_invalid_merchant_id,
    err_grpc_order_invalid_month,
    err_grpc_order_invalid_year,
    err_grpc_validate_create_order,
    err_grpc_validate_update_order,
)

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
TRASHED = datetime(2026, 2, 1, 6, 7, 8)


class FakeAbort(Exception):
    def __init__(self, code: grpc.StatusCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class FakeContext:
    def __init__(self) -> None:
        self.metadata: tuple[Any, ...] = ()
        self.aborted: FakeAbort | None = None

    def set_trailing_metadata(self, metadata: tuple[Any, ...]) -> None:
        self.metadata = metadata

    async def abort(self, code: grpc.StatusCode, message: str) -> None:
        self.aborted = FakeAbort(code, message)
        raise self.aborted


def _logger() -> Logger:
    return Logger("test", "error")


# ---- query handler ----


def _list_row(order_id: int = 1, total: int = 11) -> GetOrdersRow:
    return GetOrdersRow(
        order_id=order_id,
        user_id=5,
        merchant_id=3,
        total_price=15000,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(
    order_id: int = 1, deleted_at: datetime | None = None
) -> GetOrdersActiveRow:
    return GetOrdersActiveRow(
        order_id=order_id,
        user_id=5,
        merchant_id=3,
        total_price=15000,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=11,
    )


def _trashed_row(order_id: int = 1) -> GetOrdersTrashedRow:
    return GetOrdersTrashedRow(
        order_id=order_id,
        user_id=5,
        merchant_id=3,
        total_price=15000,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=TRASHED,
        total_count=11,
    )


class FakeQueryService:
    def __init__(self) -> None:
        self.last: Any = None

    async def find_all(self, request):
        self.last = request
        return [_list_row()], 11

    async def find_active(self, request):
        self.last = request
        return [_active_row()], 11

    async def find_trashed(self, request):
        self.last = request
        return [_trashed_row()], 11

    async def find_by_merchant(self, request):
        self.last = request
        return [_list_row()], 11

    async def find_by_id(self, order_id: int) -> OrderRow:
        self.last = order_id
        return OrderRow(
            order_id=order_id,
            user_id=5,
            merchant_id=3,
            total_price=15000,
            created_at=CREATED,
            updated_at=UPDATED,
        )


def _query_handler(service: FakeQueryService | None = None) -> OrderQueryHandler:
    return OrderQueryHandler(service or FakeQueryService(), _logger())


async def test_query_find_all_millis_and_clamps() -> None:
    service = FakeQueryService()
    response = await _query_handler(service).FindAll(
        order_query_pb2.FindAllOrderRequest(page=0, page_size=0, search="x"),
        FakeContext(),
    )
    assert response.message == "Successfully fetched order"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_records == 11
    assert response.data[0].id == 1
    assert response.data[0].merchant_id == 3
    assert response.data[0].total_price == 15000
    assert response.data[0].created_at == "2026-01-02 03:04:05.000"
    assert response.data[0].updated_at == "2026-01-03 04:05:06.000"
    assert service.last.page == 1 and service.last.page_size == 10


async def test_query_find_by_id_and_invalid_id() -> None:
    service = FakeQueryService()
    response = await _query_handler(service).FindById(
        order_common_pb2.FindByIdOrderRequest(id=7), FakeContext()
    )
    assert response.message == "Successfully fetched order"
    assert response.data.id == 7
    assert service.last == 7

    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindById(
            order_common_pb2.FindByIdOrderRequest(id=0), FakeContext()
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == err_grpc_order_invalid_id.message


async def test_query_find_by_active_leaves_deleted_at_unset() -> None:
    response = await _query_handler().FindByActive(
        order_query_pb2.FindAllOrderRequest(), FakeContext()
    )
    assert response.message == "Successfully fetched active order"
    # Active row -> wrapper NOT attached (guards on non-empty).
    assert not response.data[0].HasField("deleted_at")


async def test_query_find_by_trashed_sets_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        order_query_pb2.FindAllOrderRequest(), FakeContext()
    )
    assert response.message == "Successfully fetched trashed order"
    assert response.data[0].deleted_at.value == "2026-02-01 06:07:08.000"


# ---- command handler ----


def _order_row(order_id: int = 9) -> OrderRow:
    return OrderRow(
        order_id=order_id,
        user_id=5,
        merchant_id=3,
        total_price=15000,
        created_at=CREATED,
        updated_at=UPDATED,
    )


def _order(deleted_at: datetime | None) -> Any:
    from pkg.database.schema.order import Order

    return Order(
        order_id=7,
        user_id=5,
        merchant_id=3,
        total_price=15000,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
    )


class FakeCommandService:
    def __init__(self) -> None:
        self.last_create: Any = None
        self.last_update: Any = None
        self.calls: list[str] = []

    async def create(self, request):
        self.last_create = request
        return _order_row()

    async def update(self, request):
        self.last_update = request
        return _order_row(order_id=request.order_id or 0)

    async def trash(self, order_id):
        self.calls.append(f"trash:{order_id}")
        return _order(TRASHED)

    async def restore(self, order_id):
        self.calls.append(f"restore:{order_id}")
        return _order(None)

    async def delete_permanent(self, order_id):
        self.calls.append(f"delete:{order_id}")
        return True

    async def restore_all(self):
        self.calls.append("restore_all")
        return True

    async def delete_all(self):
        self.calls.append("delete_all")
        return True

    async def reconcile_stock_reservations(self):
        self.calls.append("reconcile")
        from service.order.service.interfaces import ReconcileResult

        return ReconcileResult()

    async def cleanup_idempotency_records(self, retention_days: int):
        self.calls.append(f"cleanup:{retention_days}")
        from service.order.service.interfaces import CleanupResult

        return CleanupResult()


def _command_handler(
    service: FakeCommandService | None = None,
) -> OrderCommandHandler:
    return OrderCommandHandler(service or FakeCommandService(), _logger())


def _valid_create_request() -> Any:
    return order_command_pb2.CreateOrderRequest(
        merchant_id=3,
        user_id=5,
        total_price=15000,
        items=[order_command_pb2.CreateOrderItemRequest(product_id=10, quantity=1, price=15000)],
        shipping=shipping_address_command_pb2.CreateShippingAddressRequest(
            alamat="Jl. Test 123",
            provinsi="DKI",
            kota="Jakarta",
            courier="JNE",
            shipping_method="REG",
            shipping_cost=2000,
            negara="Indonesia",
        ),
    )


async def test_command_create_validates_and_calls_service() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).Create(_valid_create_request(), FakeContext())
    assert response.message == "Successfully created order"
    assert response.data.id == 9
    assert service.last_create.merchant_id == 3
    assert service.last_create.user_id == 5
    assert service.last_create.total_price == 15000
    assert service.last_create.items[0].product_id == 10


async def test_command_create_validation_failure() -> None:
    # Missing merchant_id (required) -> the create sentinel.
    request = _valid_create_request()
    request.merchant_id = 0
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(request, FakeContext())
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == err_grpc_validate_create_order.message


def _valid_update_request() -> Any:
    request = order_command_pb2.UpdateOrderRequest(
        order_id=7,
        user_id=5,
        total_price=15000,
        items=[order_command_pb2.UpdateOrderItemRequest(order_item_id=1, product_id=10, quantity=1, price=15000)],
    )
    return request


async def test_command_update_without_shipping() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).Update(
        _valid_update_request(), FakeContext()
    )
    assert response.message == "Successfully updated order"
    assert service.last_update.order_id == 7
    assert service.last_update.shipping_address is None


async def test_command_update_shipping_id_maps_non_positive_to_none() -> None:
    service = FakeCommandService()
    request = _valid_update_request()
    request.shipping.shipping_id = 0
    request.shipping.alamat = "Jl. Baru 456"
    await _command_handler(service).Update(request, FakeContext())
    assert service.last_update.shipping_address is not None
    assert service.last_update.shipping_address.shipping_id is None
    assert service.last_update.shipping_address.alamat == "Jl. Baru 456"

    positive = _valid_update_request()
    positive.shipping.shipping_id = 42
    await _command_handler(service).Update(positive, FakeContext())
    assert service.last_update.shipping_address.shipping_id == 42


async def test_command_update_validation_failure() -> None:
    request = _valid_update_request()
    request.user_id = 0
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(request, FakeContext())
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == err_grpc_validate_update_order.message


async def test_command_trash_and_restore_set_deleted_at() -> None:
    service = FakeCommandService()
    trashed = await _command_handler(service).TrashedOrder(
        order_common_pb2.FindByIdOrderRequest(id=7), FakeContext()
    )
    assert trashed.message == "Successfully trashed order"
    assert trashed.data.deleted_at.value == "2026-02-01 06:07:08.000"

    restored = await _command_handler(service).RestoreOrder(
        order_common_pb2.FindByIdOrderRequest(id=7), FakeContext()
    )
    assert restored.message == "Successfully restored order"
    assert not restored.data.HasField("deleted_at")


async def test_command_single_row_guards_invalid_id() -> None:
    for rpc, request in [
        ("TrashedOrder", order_common_pb2.FindByIdOrderRequest(id=0)),
        ("RestoreOrder", order_common_pb2.FindByIdOrderRequest(id=0)),
        ("DeleteOrderPermanent", order_common_pb2.FindByIdOrderRequest(id=0)),
    ]:
        with pytest.raises(FakeAbort) as excinfo:
            await getattr(_command_handler(), rpc)(request, FakeContext())
        assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
        assert excinfo.value.message == err_grpc_order_invalid_id.message


async def test_command_delete_permanent_and_bulk() -> None:
    service = FakeCommandService()
    handler = _command_handler(service)

    deleted = await handler.DeleteOrderPermanent(
        order_common_pb2.FindByIdOrderRequest(id=7), FakeContext()
    )
    assert deleted.message == "Successfully deleted order permanently"
    assert service.calls[-1] == "delete:7"

    restored_all = await handler.RestoreAllOrder(
        order_common_pb2.FindByIdOrderRequest(), FakeContext()
    )
    assert restored_all.message == "Successfully restored all orders"

    deleted_all = await handler.DeleteAllOrderPermanent(
        order_common_pb2.FindByIdOrderRequest(), FakeContext()
    )
    assert deleted_all.message == "Successfully deleted all orders permanently"
    assert service.calls[-2:] == ["restore_all", "delete_all"]


# ---- stats handler ----


def _monthly_total_row() -> GetMonthlyTotalRevenueRow:
    return GetMonthlyTotalRevenueRow(year="2026", month="1", total_revenue=12345)


def _yearly_total_row() -> GetYearlyTotalRevenueRow:
    return GetYearlyTotalRevenueRow(year="2026", total_revenue=99999)


def _monthly_order_row() -> GetMonthlyOrderRow:
    return GetMonthlyOrderRow(
        month="1", order_count=4, total_revenue=5000.0, total_items_sold=9
    )


def _yearly_order_row() -> GetYearlyOrderRow:
    return GetYearlyOrderRow(
        year="2026",
        order_count=40,
        total_revenue=50000.0,
        total_items_sold=90,
        unique_products_sold=7,
    )


class FakeStatsService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def find_monthly_total_revenue(self, request):
        self.calls.append("monthly_total")
        return [_monthly_total_row()]

    async def find_yearly_total_revenue(self, year):
        self.calls.append(f"yearly_total:{year}")
        return [_yearly_total_row()]

    async def find_monthly_order(self, year):
        self.calls.append(f"monthly_order:{year}")
        return [_monthly_order_row()]

    async def find_yearly_order(self, year):
        self.calls.append(f"yearly_order:{year}")
        return [_yearly_order_row()]


class FakeStatsByMerchantService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def find_monthly_total_revenue_by_merchant(self, request):
        self.calls.append(f"m_total:{request.merchant_id}")
        return [_monthly_total_row()]

    async def find_yearly_total_revenue_by_merchant(self, request):
        self.calls.append(f"y_total:{request.merchant_id}")
        return [_yearly_total_row()]

    async def find_monthly_order_by_merchant(self, request):
        self.calls.append(f"m_order:{request.merchant_id}")
        return [_monthly_order_row()]

    async def find_yearly_order_by_merchant(self, request):
        self.calls.append(f"y_order:{request.merchant_id}")
        return [_yearly_order_row()]


def _stats_handler() -> tuple[OrderStatsHandler, FakeStatsService, FakeStatsByMerchantService]:
    stats = FakeStatsService()
    by_merchant = FakeStatsByMerchantService()
    return OrderStatsHandler(stats, by_merchant, _logger()), stats, by_merchant


async def test_stats_monthly_total_revenue_maps_strings_and_guards() -> None:
    handler, stats, _ = _stats_handler()
    response = await handler.FindMonthlyTotalRevenue(
        order_stats_pb2.FindYearMonthTotalRevenue(year=2026, month=1), FakeContext()
    )
    assert response.message == "Monthly sales retrieved successfully"
    assert response.data[0].year == "2026"
    assert response.data[0].month == "1"
    assert response.data[0].total_revenue == 12345
    assert stats.calls == ["monthly_total"]

    with pytest.raises(FakeAbort) as bad_year:
        await handler.FindMonthlyTotalRevenue(
            order_stats_pb2.FindYearMonthTotalRevenue(year=0, month=1), FakeContext()
        )
    assert bad_year.value.message == err_grpc_order_invalid_year.message

    with pytest.raises(FakeAbort) as bad_month:
        await handler.FindMonthlyTotalRevenue(
            order_stats_pb2.FindYearMonthTotalRevenue(year=2026, month=13),
            FakeContext(),
        )
    assert bad_month.value.message == err_grpc_order_invalid_month.message


async def test_stats_yearly_total_revenue_guards_year() -> None:
    handler, stats, _ = _stats_handler()
    response = await handler.FindYearlyTotalRevenue(
        order_stats_pb2.FindYearTotalRevenue(year=2026), FakeContext()
    )
    assert response.data[0].year == "2026"
    assert response.data[0].total_revenue == 99999
    assert stats.calls == ["yearly_total:2026"]

    with pytest.raises(FakeAbort) as bad_year:
        await handler.FindYearlyTotalRevenue(
            order_stats_pb2.FindYearTotalRevenue(year=0), FakeContext()
        )
    assert bad_year.value.message == err_grpc_order_invalid_year.message


async def test_stats_revenue_uses_invalid_id_for_bad_year() -> None:
    handler, _, _ = _stats_handler()
    with pytest.raises(FakeAbort) as bad_year:
        await handler.FindMonthlyRevenue(
            order_stats_pb2.FindYearOrder(year=0), FakeContext()
        )
    assert bad_year.value.message == err_grpc_order_invalid_id.message

    with pytest.raises(FakeAbort) as bad_year2:
        await handler.FindYearlyRevenue(
            order_stats_pb2.FindYearOrder(year=0), FakeContext()
        )
    assert bad_year2.value.message == err_grpc_order_invalid_id.message


async def test_stats_monthly_and_yearly_revenue_map_rows() -> None:
    handler, stats, _ = _stats_handler()
    monthly = await handler.FindMonthlyRevenue(
        order_stats_pb2.FindYearOrder(year=2026), FakeContext()
    )
    assert monthly.data[0].month == "1"
    assert monthly.data[0].order_count == 4
    assert monthly.data[0].total_revenue == 5000
    assert monthly.data[0].total_items_sold == 9

    yearly = await handler.FindYearlyRevenue(
        order_stats_pb2.FindYearOrder(year=2026), FakeContext()
    )
    assert yearly.data[0].year == "2026"
    assert yearly.data[0].unique_products_sold == 7
    assert stats.calls == ["monthly_order:2026", "yearly_order:2026"]


async def test_stats_by_merchant_total_revenue() -> None:
    handler, _, by_merchant = _stats_handler()
    monthly = await handler.FindMonthlyTotalRevenueByMerchant(
        order_statsbymerchant_pb2.FindYearMonthTotalRevenueByMerchant(
            year=2026, month=1, merchant_id=3
        ),
        FakeContext(),
    )
    assert monthly.message == "Monthly sales retrieved successfully"
    assert by_merchant.calls == ["m_total:3"]

    yearly = await handler.FindYearlyTotalRevenueByMerchant(
        order_statsbymerchant_pb2.FindYearTotalRevenueByMerchant(
            year=2026, merchant_id=3
        ),
        FakeContext(),
    )
    assert yearly.message == "Yearly payment methods retrieved successfully"

    with pytest.raises(FakeAbort) as bad_merchant:
        await handler.FindMonthlyTotalRevenueByMerchant(
            order_statsbymerchant_pb2.FindYearMonthTotalRevenueByMerchant(
                year=2026, month=1, merchant_id=0
            ),
            FakeContext(),
        )
    assert bad_merchant.value.message == err_grpc_order_invalid_merchant_id.message


async def test_stats_by_merchant_revenue_and_yearly_quirk() -> None:
    handler, _, by_merchant = _stats_handler()
    monthly = await handler.FindMonthlyRevenueByMerchant(
        order_statsbymerchant_pb2.FindYearOrderByMerchant(year=2026, merchant_id=3),
        FakeContext(),
    )
    assert monthly.message == "Monthly revenue by merchant data retrieved"

    yearly = await handler.FindYearlyRevenueByMerchant(
        order_statsbymerchant_pb2.FindYearOrderByMerchant(year=2026, merchant_id=3),
        FakeContext(),
    )
    assert yearly.message == "Yearly revenue by merchant data retrieved"
    assert by_merchant.calls == ["m_order:3", "y_order:3"]

    with pytest.raises(FakeAbort) as bad_merchant:
        await handler.FindYearlyRevenueByMerchant(
            order_statsbymerchant_pb2.FindYearOrderByMerchant(year=2026, merchant_id=0),
            FakeContext(),
        )
    assert bad_merchant.value.message == err_grpc_order_invalid_id.message


__all__ = []
