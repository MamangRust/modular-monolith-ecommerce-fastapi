"""Order item gRPC integration tests: real grpc.aio server, generated client.

Marked `integration`. Verifies the wire contract (millisecond timestamps, the
`deleted_at` wrapper only on the `...DeleteAt` projections) and that the
`ErrorResponse` detail survives the hop, so a 400/404 stays a 400/404."""

from __future__ import annotations

import grpc
import pytest

from pb.order_item import (
    order_item_command_pb2,
    order_item_command_pb2_grpc,
    order_item_common_pb2,
    order_item_query_pb2,
    order_item_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


async def _seed_order(db: Database, parents) -> int:
    order = await db.execute(
        """
        INSERT INTO orders (user_id, merchant_id, total_price)
        VALUES (:user_id, :merchant_id, 0)
        RETURNING order_id
        """,
        {"user_id": parents.user_id, "merchant_id": parents.merchant_id},
    )
    assert order is not None
    return int(order["order_id"])


async def test_order_item_grpc_lifecycle_and_error_mapping(
    db: Database, order_parents, order_item_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(order_item_grpc_server)
    query = order_item_query_pb2_grpc.OrderItemQueryServiceStub(channel)
    command = order_item_command_pb2_grpc.OrderItemCommandServiceStub(channel)
    order_id = await _seed_order(db, order_parents)
    product_id = order_parents.product_id

    created = await command.CreateOrderItem(
        order_item_command_pb2.CreateOrderItemRecordRequest(
            order_id=order_id, product_id=product_id, quantity=2, price=5000
        ),
        timeout=5,
    )
    assert created.status == "success"
    assert created.message == "Successfully created order item"
    assert created.data.order_id == order_id
    assert created.data.product_id == product_id
    assert created.data.created_at  # millisecond layout, non-empty
    item_id = created.data.id

    found = await query.FindOrderItemByOrder(
        order_item_common_pb2.FindByIdOrderItemRequest(id=order_id), timeout=5
    )
    assert found.message == "Successfully fetched order items by order"
    assert any(row.id == item_id for row in found.data)

    listed = await query.FindAll(
        order_item_query_pb2.FindAllOrderItemRequest(
            page=1, page_size=10, search=str(product_id)
        ),
        timeout=5,
    )
    assert listed.pagination.total_records >= 1

    trashed = await command.TrashOrderItem(
        order_item_common_pb2.FindByIdOrderItemRequest(id=item_id), timeout=5
    )
    assert trashed.message == "Successfully trashed order item"

    # FindAll filters `deleted_at IS NULL`, so the trashed row is gone.
    listed_after = await query.FindAll(
        order_item_query_pb2.FindAllOrderItemRequest(
            page=1, page_size=10, search=str(product_id)
        ),
        timeout=5,
    )
    assert all(row.id != item_id for row in listed_after.data)

    trashed_rows = await query.FindByTrashed(
        order_item_query_pb2.FindAllOrderItemRequest(
            page=1, page_size=10, search=str(product_id)
        ),
        timeout=5,
    )
    assert any(
        row.id == item_id and row.deleted_at.value for row in trashed_rows.data
    )

    restored = await command.RestoreOrderItem(
        order_item_common_pb2.FindByIdOrderItemRequest(id=item_id), timeout=5
    )
    assert restored.message == "Successfully restored order item"

    total = await command.CalculateTotalPrice(
        order_item_command_pb2.CalculateTotalPriceRequest(order_id=order_id),
        timeout=5,
    )
    assert total.status == "success"
    assert total.total_price == 2 * 5000

    with pytest.raises(grpc.aio.AioRpcError) as invalid:
        await command.TrashOrderItem(
            order_item_common_pb2.FindByIdOrderItemRequest(id=0), timeout=5
        )
    assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
    parsed_invalid = parse_grpc_error(invalid.value)
    assert parsed_invalid.code == 400
    assert parsed_invalid.message == "invalid ID"

    with pytest.raises(grpc.aio.AioRpcError) as invalid_create:
        await command.CreateOrderItem(
            order_item_command_pb2.CreateOrderItemRecordRequest(
                order_id=order_id, product_id=product_id, quantity=0, price=5000
            ),
            timeout=5,
        )
    assert invalid_create.value.code() is grpc.StatusCode.INVALID_ARGUMENT
    assert parse_grpc_error(invalid_create.value).message == "invalid ID"

    # A repository 404 is preserved as NOT_FOUND (ToGrpcError semantics).
    with pytest.raises(grpc.aio.AioRpcError) as missing:
        await command.TrashOrderItem(
            order_item_common_pb2.FindByIdOrderItemRequest(id=2_000_000_000),
            timeout=5,
        )
    assert missing.value.code() is grpc.StatusCode.NOT_FOUND
    assert parse_grpc_error(missing.value).code == 404

    await command.TrashOrderItem(
        order_item_common_pb2.FindByIdOrderItemRequest(id=item_id), timeout=5
    )
    deleted = await command.DeleteOrderItemPermanent(
        order_item_common_pb2.FindByIdOrderItemRequest(id=item_id), timeout=5
    )
    assert deleted.message == "Successfully deleted order item permanently"
    await channel.close()


async def test_delete_by_order_permanent_over_grpc(
    db: Database, order_parents, order_item_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(order_item_grpc_server)
    query = order_item_query_pb2_grpc.OrderItemQueryServiceStub(channel)
    command = order_item_command_pb2_grpc.OrderItemCommandServiceStub(channel)
    order_id = await _seed_order(db, order_parents)

    await command.CreateOrderItem(
        order_item_command_pb2.CreateOrderItemRecordRequest(
            order_id=order_id, product_id=order_parents.product_id, quantity=1, price=100
        ),
        timeout=5,
    )
    deleted = await command.DeleteOrderItemByOrderPermanent(
        order_item_common_pb2.FindByIdOrderItemRequest(id=order_id), timeout=5
    )
    assert (
        deleted.message
        == "Successfully deleted order items by order permanently"
    )

    found = await query.FindOrderItemByOrder(
        order_item_common_pb2.FindByIdOrderItemRequest(id=order_id), timeout=5
    )
    assert list(found.data) == []
    await channel.close()
