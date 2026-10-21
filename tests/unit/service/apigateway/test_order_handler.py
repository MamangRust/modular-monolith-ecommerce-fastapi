"""Unit tests for the gateway order transport handler. `normalize_pagination` Matches the expected gateway clamp. keeps no gateway-level cache. The order gateway reads `merchant_id`/`user_id` from the **body** (binds the whole request), never the JWT subject, so `create` does not require an authenticated subject."""

from __future__ import annotations

from typing import Any

import grpc
import pytest

from pb.order import order_command_pb2, order_common_pb2, order_query_pb2
from pb.order.stats import order_stats_pb2, order_statsbymerchant_pb2
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler.order.handler import (
    OrderHandler,
    normalize_pagination,
)
from shared.domain.requests.order import (
    CreateOrderItemRequest,
    CreateOrderRequest,
    UpdateOrderItemRequest,
    UpdateOrderRequest,
)
from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    UpdateShippingAddressRequest,
)
from shared.errors import AppError


def _rpc_error(code: grpc.StatusCode, details: str) -> grpc.aio.AioRpcError:
    return grpc.aio.AioRpcError(
        code, grpc.aio.Metadata(), grpc.aio.Metadata(), details=details
    )


class FakeQuery:
    def __init__(self) -> None:
        self.last: Any = None

    async def FindAll(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponsePaginationOrder(
            status="success", message="Successfully fetched order"
        )
        message.data.add(
            id=1,
            merchant_id=3,
            user_id=5,
            total_price=15000,
            created_at="2026-01-02 03:04:05.000",
            updated_at="2026-01-03 04:05:06.000",
        )
        message.pagination.total_records = 1
        return message

    async def FindById(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponseOrder(
            status="success", message="Successfully fetched order"
        )
        message.data.id = request.id
        return message

    async def FindByActive(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponsePaginationOrderDeleteAt(
            status="success", message="Successfully fetched active order"
        )
        message.data.add(id=1, created_at="2026-01-02 03:04:05.000")
        return message

    async def FindByTrashed(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponsePaginationOrderDeleteAt(
            status="success", message="Successfully fetched trashed order"
        )
        row = message.data.add(id=1)
        row.deleted_at.value = "2026-02-01 06:07:08.000"
        return message


class FakeCommand:
    def __init__(self, fail_create: bool = False) -> None:
        self.last: Any = None
        self.fail_create = fail_create

    async def Create(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        if self.fail_create:
            raise _rpc_error(grpc.StatusCode.NOT_FOUND, "product not found")
        message = order_common_pb2.ApiResponseOrder(
            status="success", message="Successfully created order"
        )
        message.data.id = 9
        message.data.merchant_id = request.merchant_id
        return message

    async def Update(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponseOrder(
            status="success", message="Successfully updated order"
        )
        message.data.id = request.order_id
        return message

    async def TrashedOrder(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        return order_common_pb2.ApiResponseOrderDeleteAt(
            status="success", message="Successfully trashed order"
        )

    async def RestoreOrder(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        return order_common_pb2.ApiResponseOrderDeleteAt(
            status="success", message="Successfully restored order"
        )

    async def DeleteOrderPermanent(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        return order_common_pb2.ApiResponseOrderDelete(
            status="success", message="Successfully deleted order permanently"
        )

    async def RestoreAllOrder(self, request: Any, timeout: float | None = None) -> Any:
        self.last = request
        return order_common_pb2.ApiResponseOrderAll(
            status="success", message="Successfully restored all orders"
        )

    async def DeleteAllOrderPermanent(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        return order_common_pb2.ApiResponseOrderAll(
            status="success", message="Successfully deleted all orders permanently"
        )


class FakeStats:
    def __init__(self) -> None:
        self.last: Any = None

    async def FindMonthlyTotalRevenue(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponseOrderMonthlyTotalRevenue(
            status="success", message="Monthly sales retrieved successfully"
        )
        message.data.add(year="2026", month="1", total_revenue=12345)
        return message

    async def FindYearlyTotalRevenue(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponseOrderYearlyTotalRevenue(
            status="success", message="ok"
        )
        message.data.add(year="2026", total_revenue=99999)
        return message

    async def FindMonthlyRevenue(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponseOrderMonthly(status="success", message="ok")
        message.data.add(month="1", order_count=4, total_revenue=5000, total_items_sold=9)
        return message

    async def FindYearlyRevenue(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponseOrderYearly(status="success", message="ok")
        message.data.add(
            year="2026",
            order_count=40,
            total_revenue=50000,
            total_items_sold=90,
            unique_products_sold=7,
        )
        return message


class FakeStatsByMerchant:
    def __init__(self) -> None:
        self.last: Any = None

    async def FindMonthlyTotalRevenueByMerchant(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponseOrderMonthlyTotalRevenue(
            status="success", message="ok"
        )
        message.data.add(year="2026", month="1", total_revenue=12345)
        return message

    async def FindYearlyTotalRevenueByMerchant(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponseOrderYearlyTotalRevenue(
            status="success", message="ok"
        )
        message.data.add(year="2026", total_revenue=99999)
        return message

    async def FindMonthlyRevenueByMerchant(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponseOrderMonthly(status="success", message="ok")
        message.data.add(month="1", order_count=4, total_revenue=5000, total_items_sold=9)
        return message

    async def FindYearlyRevenueByMerchant(
        self, request: Any, timeout: float | None = None
    ) -> Any:
        self.last = request
        message = order_common_pb2.ApiResponseOrderYearly(status="success", message="ok")
        message.data.add(
            year="2026",
            order_count=40,
            total_revenue=50000,
            total_items_sold=90,
            unique_products_sold=7,
        )
        return message


def _handler() -> tuple[OrderHandler, grpc.aio.Channel]:
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    connections = ServiceConnections(
        channels={"order": channel},
        addresses={"order": "127.0.0.1:1"},
    )
    return OrderHandler(connections), channel


@pytest.mark.parametrize(
    ("page", "page_size", "expected"),
    [
        (1, 10, (1, 10)),
        (0, 0, (1, 10)),
        (-5, -1, (1, 10)),
        (3, 0, (3, 10)),
        (0, 25, (1, 25)),
    ],
)
def test_normalize_pagination(page: int, page_size: int, expected: tuple[int, int]) -> None:
    assert normalize_pagination(page, page_size) == expected


async def test_query_methods_build_requests_and_map() -> None:
    handler, channel = _handler()
    fake: Any = FakeQuery()
    handler._query = fake
    try:
        response = await handler.find_all(0, 0, "x")
        assert isinstance(fake.last, order_query_pb2.FindAllOrderRequest)
        assert fake.last.page == 1 and fake.last.page_size == 10
        assert fake.last.search == "x"
        assert response.message == "Successfully fetched order"
        assert response.data is not None
        assert response.data[0].id == 1
        assert response.data[0].created_at == "2026-01-02 03:04:05.000"
        assert response.pagination.total_records == 1

        by_id = await handler.find_by_id(7)
        assert isinstance(fake.last, order_common_pb2.FindByIdOrderRequest)
        assert fake.last.id == 7
        assert by_id.data is not None and by_id.data.id == 7

        await handler.find_by_active(1, 10, "")
        assert isinstance(fake.last, order_query_pb2.FindAllOrderRequest)

        await handler.find_by_trashed(1, 10, "")
        assert isinstance(fake.last, order_query_pb2.FindAllOrderRequest)
    finally:
        await channel.close()


async def test_create_builds_body_request_and_maps() -> None:
    handler, channel = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        body = CreateOrderRequest(
            merchant_id=3,
            user_id=5,
            total_price=15000,
            items=[CreateOrderItemRequest(product_id=10, quantity=1, price=15000)],
            shipping_address=CreateShippingAddressRequest(
                alamat="Jl. Test 123",
                provinsi="DKI",
                kota="Jakarta",
                courier="JNE",
                shipping_method="REG",
                shipping_cost=2000,
                negara="Indonesia",
            ),
        )
        response = await handler.create(body)
        assert isinstance(fake.last, order_command_pb2.CreateOrderRequest)
        assert fake.last.merchant_id == 3
        assert fake.last.user_id == 5
        assert fake.last.total_price == 15000
        assert fake.last.items[0].product_id == 10
        assert fake.last.shipping.alamat == "Jl. Test 123"
        assert fake.last.shipping.shipping_cost == 2000
        assert response.data is not None
        assert response.data.id == 9
    finally:
        await channel.close()


async def test_create_maps_grpc_error() -> None:
    handler, channel = _handler()
    handler._command = FakeCommand(fail_create=True)
    try:
        body = CreateOrderRequest(
            merchant_id=3,
            user_id=5,
            total_price=15000,
            items=[CreateOrderItemRequest(product_id=10, quantity=1, price=15000)],
            shipping_address=CreateShippingAddressRequest(
                alamat="Jl. Test 123",
                provinsi="DKI",
                kota="Jakarta",
                courier="JNE",
                shipping_method="REG",
                shipping_cost=2000,
                negara="Indonesia",
            ),
        )
        with pytest.raises(AppError) as excinfo:
            await handler.create(body)
        assert excinfo.value.code == 404
        assert excinfo.value.message == "product not found"
    finally:
        await channel.close()


async def test_update_uses_path_id_and_shipping_rules() -> None:
    handler, channel = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        body = UpdateOrderRequest(
            order_id=999,  # ignored: the path id wins
            user_id=5,
            total_price=15000,
            items=[
                UpdateOrderItemRequest(
                    order_item_id=1, product_id=10, quantity=1, price=15000
                )
            ],
        )
        await handler.update(7, body)
        assert isinstance(fake.last, order_command_pb2.UpdateOrderRequest)
        assert fake.last.order_id == 7
        assert not fake.last.HasField("shipping")

        with_shipping = UpdateOrderRequest(
            user_id=5,
            total_price=15000,
            items=[
                UpdateOrderItemRequest(
                    order_item_id=1, product_id=10, quantity=1, price=15000
                )
            ],
            shipping_address=UpdateShippingAddressRequest(
                shipping_id=None,
                alamat="Jl. Baru 456",
                provinsi="DKI",
                kota="Jakarta",
                courier="JNE",
                shipping_method="REG",
                shipping_cost=2000,
                negara="Indonesia",
            ),
        )
        await handler.update(7, with_shipping)
        assert fake.last.HasField("shipping")
        assert fake.last.shipping.shipping_id == 0  # pointerValue(None)
        assert fake.last.shipping.alamat == "Jl. Baru 456"
    finally:
        await channel.close()


async def test_command_single_row_and_bulk_methods() -> None:
    handler, channel = _handler()
    fake: Any = FakeCommand()
    handler._command = fake
    try:
        for method, message in [
            ("trash", "Successfully trashed order"),
            ("restore", "Successfully restored order"),
        ]:
            response = await getattr(handler, method)(7)
            assert isinstance(fake.last, order_common_pb2.FindByIdOrderRequest)
            assert fake.last.id == 7
            assert response.message == message

        deleted = await handler.delete_permanent(7)
        assert deleted.message == "Successfully deleted order permanently"

        restored_all = await handler.restore_all()
        assert restored_all.message == "Successfully restored all orders"

        deleted_all = await handler.delete_all_permanent()
        assert deleted_all.message == "Successfully deleted all orders permanently"
    finally:
        await channel.close()


async def test_stats_methods_build_requests_and_map() -> None:
    handler, channel = _handler()
    stats: Any = FakeStats()
    by_merchant: Any = FakeStatsByMerchant()
    handler._stats = stats
    handler._stats_by_merchant = by_merchant
    try:
        monthly = await handler.find_monthly_total_revenue(2026, 1)
        assert isinstance(stats.last, order_stats_pb2.FindYearMonthTotalRevenue)
        assert stats.last.year == 2026 and stats.last.month == 1
        assert monthly.data is not None
        assert monthly.data[0].total_revenue == 12345

        await handler.find_yearly_total_revenue(2026)
        assert isinstance(stats.last, order_stats_pb2.FindYearTotalRevenue)

        await handler.find_monthly_revenue(2026)
        assert isinstance(stats.last, order_stats_pb2.FindYearOrder)

        await handler.find_yearly_revenue(2026)
        assert isinstance(stats.last, order_stats_pb2.FindYearOrder)

        await handler.find_monthly_total_revenue_by_merchant(2026, 1, 3)
        assert isinstance(
            by_merchant.last,
            order_statsbymerchant_pb2.FindYearMonthTotalRevenueByMerchant,
        )
        assert by_merchant.last.merchant_id == 3

        await handler.find_yearly_total_revenue_by_merchant(2026, 3)
        assert isinstance(
            by_merchant.last,
            order_statsbymerchant_pb2.FindYearTotalRevenueByMerchant,
        )

        await handler.find_monthly_revenue_by_merchant(2026, 3)
        assert isinstance(
            by_merchant.last, order_statsbymerchant_pb2.FindYearOrderByMerchant
        )

        await handler.find_yearly_revenue_by_merchant(2026, 3)
        assert isinstance(
            by_merchant.last, order_statsbymerchant_pb2.FindYearOrderByMerchant
        )
    finally:
        await channel.close()


__all__ = []
