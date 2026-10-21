"""Unit tests for order item gRPC handlers (in-process, no server/DB)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest

from pb.order_item import (
    order_item_command_pb2,
    order_item_common_pb2,
    order_item_query_pb2,
)
from pkg.database.schema.order_item import (
    CreateOrderItemRow,
    GetOrderItemsActiveRow,
    GetOrderItemsByOrderRow,
    GetOrderItemsRow,
    OrderItem,
    UpdateOrderItemRow,
)
from pkg.logger.logger import Logger
from service.order_item.handler.command import OrderItemCommandHandler
from service.order_item.handler.query import OrderItemQueryHandler

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 3, 11, 22, 33)


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


def _row(order_item_id: int = 1, total: int = 11) -> GetOrderItemsRow:
    return GetOrderItemsRow(
        order_item_id=order_item_id,
        order_id=10,
        product_id=20,
        quantity=2,
        price=5000,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(deleted_at: datetime | None = None) -> GetOrderItemsActiveRow:
    return GetOrderItemsActiveRow(
        order_item_id=1,
        order_id=10,
        product_id=20,
        quantity=2,
        price=5000,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=1,
    )


def _by_order_row(order_item_id: int = 1) -> GetOrderItemsByOrderRow:
    return GetOrderItemsByOrderRow(
        order_item_id=order_item_id,
        order_id=10,
        product_id=20,
        quantity=2,
        price=5000,
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeQueryService:
    async def find_all(self, search, page, page_size):
        return [_row()], 11

    async def find_active(self, search, page, page_size):
        return [_active_row()], 1

    async def find_trashed(self, search, page, page_size):
        return [_active_row(deleted_at=DELETED)], 1

    async def find_by_order(self, order_id):
        return [_by_order_row()]


class FakeCommandService:
    async def create(self, request):
        return CreateOrderItemRow(
            order_item_id=1,
            order_id=request.order_id,
            product_id=request.product_id,
            quantity=request.quantity,
            price=request.price,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        return UpdateOrderItemRow(
            order_item_id=request.order_item_id,
            order_id=10,
            product_id=20,
            quantity=request.quantity,
            price=request.price,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, order_item_id):
        return OrderItem(
            order_item_id=order_item_id,
            order_id=10,
            product_id=20,
            quantity=2,
            price=5000,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, order_item_id):
        return OrderItem(
            order_item_id=order_item_id,
            order_id=10,
            product_id=20,
            quantity=2,
            price=5000,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, order_item_id):
        return True

    async def delete_by_order_permanent(self, order_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all(self):
        return True

    async def calculate_total_price(self, order_id):
        return 12345


def _logger() -> Logger:
    return Logger("test", "error")


def _query_handler() -> OrderItemQueryHandler:
    return OrderItemQueryHandler(FakeQueryService(), _logger())


def _command_handler() -> OrderItemCommandHandler:
    return OrderItemCommandHandler(FakeCommandService(), _logger())


async def test_find_all_normalizes_and_computes_total_pages() -> None:
    request = order_item_query_pb2.FindAllOrderItemRequest(
        page=0, page_size=0, search=""
    )
    response = await _query_handler().FindAll(request, FakeContext())

    assert response.status == "success"
    assert response.message == "Successfully fetched order items"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_pages == 2
    assert response.pagination.total_records == 11
    # Millisecond layout, like banner (not category's date-only).
    assert response.data[0].created_at == "2026-01-02 03:04:05.000"


async def test_find_by_active_omits_deleted_at_wrapper_when_null() -> None:
    response = await _query_handler().FindByActive(
        order_item_query_pb2.FindAllOrderItemRequest(page=1, page_size=10),
        FakeContext(),
    )
    assert response.message == "Successfully fetched active order items"
    # Order item (unlike category) attaches the wrapper only when non-empty.
    assert response.data[0].HasField("deleted_at") is False


async def test_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        order_item_query_pb2.FindAllOrderItemRequest(page=1, page_size=10),
        FakeContext(),
    )
    assert response.message == "Successfully fetched trashed order items"
    assert response.data[0].HasField("deleted_at") is True
    assert response.data[0].deleted_at.value == "2026-02-03 11:22:33.000"


async def test_find_order_item_by_order_returns_list() -> None:
    response = await _query_handler().FindOrderItemByOrder(
        order_item_common_pb2.FindByIdOrderItemRequest(id=10), FakeContext()
    )
    assert response.message == "Successfully fetched order items by order"
    assert response.data[0].order_id == 10


async def test_find_order_item_by_order_zero_id_is_allowed() -> None:
    # performs no zero-id guard on this route; id=0 simply yields an empty
    # list. The fake ignores the id, so the call must succeed.
    response = await _query_handler().FindOrderItemByOrder(
        order_item_common_pb2.FindByIdOrderItemRequest(id=0), FakeContext()
    )
    assert response.status == "success"


async def test_create_order_item_rejects_invalid_quantity() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().CreateOrderItem(
            order_item_command_pb2.CreateOrderItemRecordRequest(
                order_id=10, product_id=20, quantity=0, price=5000
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"
    assert context.metadata


async def test_create_order_item_success() -> None:
    response = await _command_handler().CreateOrderItem(
        order_item_command_pb2.CreateOrderItemRecordRequest(
            order_id=10, product_id=20, quantity=2, price=5000
        ),
        FakeContext(),
    )
    assert response.message == "Successfully created order item"
    assert response.data.order_id == 10
    assert response.data.price == 5000


async def test_update_order_item_success() -> None:
    response = await _command_handler().UpdateOrderItem(
        order_item_command_pb2.UpdateOrderItemRecordRequest(
            order_item_id=1, quantity=3, price=6000
        ),
        FakeContext(),
    )
    assert response.message == "Successfully updated order item"
    assert response.data.quantity == 3


async def test_trash_order_item_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().TrashOrderItem(
            order_item_common_pb2.FindByIdOrderItemRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"


async def test_trash_order_item_returns_delete_at_shape() -> None:
    response = await _command_handler().TrashOrderItem(
        order_item_common_pb2.FindByIdOrderItemRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully trashed order item"
    assert response.data.id == 1


async def test_delete_order_item_permanent() -> None:
    response = await _command_handler().DeleteOrderItemPermanent(
        order_item_common_pb2.FindByIdOrderItemRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully deleted order item permanently"


async def test_restore_all_orders_item() -> None:
    from google.protobuf import empty_pb2

    response = await _command_handler().RestoreAllOrdersItem(
        empty_pb2.Empty(), FakeContext()
    )
    assert response.message == "Successfully restored all order items"


async def test_delete_all_permanent_orders_item() -> None:
    from google.protobuf import empty_pb2

    response = await _command_handler().DeleteAllPermanentOrdersItem(
        empty_pb2.Empty(), FakeContext()
    )
    assert response.message == "Successfully deleted all order items permanently"


async def test_delete_order_item_by_order_permanent() -> None:
    response = await _command_handler().DeleteOrderItemByOrderPermanent(
        order_item_common_pb2.FindByIdOrderItemRequest(id=7), FakeContext()
    )
    assert (
        response.message == "Successfully deleted order items by order permanently"
    )


async def test_calculate_total_price() -> None:
    response = await _command_handler().CalculateTotalPrice(
        order_item_command_pb2.CalculateTotalPriceRequest(order_id=10),
        FakeContext(),
    )
    assert response.status == "success"
    assert response.message == "Successfully calculated total price"
    assert response.total_price == 12345


async def test_calculate_total_price_rejects_zero_order_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().CalculateTotalPrice(
            order_item_command_pb2.CalculateTotalPriceRequest(order_id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID"
