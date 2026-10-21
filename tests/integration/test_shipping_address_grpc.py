"""Shipping address gRPC integration tests: real grpc.aio server, generated client. Marked `integration`. Verifies the wire contract (date-only timestamps, the `deleted_at` wrapper only on the `.DeleteAt` projections, `shipping_cost` as an, `courier` present on the gRPC message) and that the `ErrorResponse` detail survives the hop, so a 400/404 stays a 400/404."""

from __future__ import annotations

import uuid

import grpc
import pytest

from pb.shipping_address import (
    shipping_address_command_pb2,
    shipping_address_command_pb2_grpc,
    shipping_address_common_pb2,
    shipping_address_query_pb2,
    shipping_address_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


def _alamat() -> str:
    return f"Jalan Uji {uuid.uuid4().hex[:10]}"


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


async def test_shipping_address_grpc_lifecycle_and_error_mapping(
    db: Database, order_parents, shipping_address_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(shipping_address_grpc_server)
    query = shipping_address_query_pb2_grpc.ShippingQueryServiceStub(channel)
    command = shipping_address_command_pb2_grpc.ShippingCommandServiceStub(channel)
    order_id = await _seed_order(db, order_parents)
    alamat = _alamat()

    created = await command.CreateShipping(
        shipping_address_command_pb2.CreateShippingAddressRequest(
            order_id=order_id,
            alamat=alamat,
            provinsi="DKI Jakarta",
            kota="Jakarta",
            courier="JNE",
            shipping_method="REG",
            shipping_cost=12000,
            negara="Indonesia",
        ),
        timeout=5,
    )
    assert created.status == "success"
    assert created.message == "Successfully created shipping address"
    assert created.data.order_id == order_id
    assert created.data.alamat == alamat
    assert created.data.shippingCost == 12000
    assert created.data.courier == "JNE"
    # Date-only layout, non-empty.
    assert created.data.created_at
    assert len(created.data.created_at) == 10
    shipping_id = created.data.id

    found = await query.FindById(
        shipping_address_common_pb2.FindByIdShippingRequest(id=shipping_id),
        timeout=5,
    )
    assert found.message == "Successfully fetched shipping address"
    assert found.data.id == shipping_id

    by_order = await query.FindByOrder(
        shipping_address_common_pb2.FindByIdShippingRequest(id=order_id),
        timeout=5,
    )
    assert by_order.message == "Successfully fetched shipping address by order ID"
    assert by_order.data.order_id == order_id

    listed = await query.FindAll(
        shipping_address_query_pb2.FindAllShippingRequest(
            page=1, page_size=10, search=alamat
        ),
        timeout=5,
    )
    assert listed.pagination.total_records >= 1

    trashed = await command.TrashedShipping(
        shipping_address_common_pb2.FindByIdShippingRequest(id=shipping_id),
        timeout=5,
    )
    assert trashed.message == "Successfully trashed shipping address"
    assert trashed.data.deleted_at.value

    # FindAll filters `deleted_at IS NULL`, so the trashed row is gone.
    listed_after = await query.FindAll(
        shipping_address_query_pb2.FindAllShippingRequest(
            page=1, page_size=10, search=alamat
        ),
        timeout=5,
    )
    assert all(row.id != shipping_id for row in listed_after.data)

    trashed_rows = await query.FindByTrashed(
        shipping_address_query_pb2.FindAllShippingRequest(
            page=1, page_size=10, search=alamat
        ),
        timeout=5,
    )
    assert any(
        row.id == shipping_id and row.deleted_at.value for row in trashed_rows.data
    )

    restored = await command.RestoreShipping(
        shipping_address_common_pb2.FindByIdShippingRequest(id=shipping_id),
        timeout=5,
    )
    assert restored.message == "Successfully restored shipping address"

    with pytest.raises(grpc.aio.AioRpcError) as invalid:
        await command.TrashedShipping(
            shipping_address_common_pb2.FindByIdShippingRequest(id=0), timeout=5
        )
    assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
    parsed_invalid = parse_grpc_error(invalid.value)
    assert parsed_invalid.code == 400
    assert parsed_invalid.message == "invalid ID"

    with pytest.raises(grpc.aio.AioRpcError) as invalid_query:
        await query.FindById(
            shipping_address_common_pb2.FindByIdShippingRequest(id=0), timeout=5
        )
    assert invalid_query.value.code() is grpc.StatusCode.INVALID_ARGUMENT

    # A repository 404 is preserved as NOT_FOUND (ToGrpcError semantics).
    with pytest.raises(grpc.aio.AioRpcError) as missing:
        await command.TrashedShipping(
            shipping_address_common_pb2.FindByIdShippingRequest(id=2_000_000_000),
            timeout=5,
        )
    assert missing.value.code() is grpc.StatusCode.NOT_FOUND
    assert parse_grpc_error(missing.value).code == 404

    await command.TrashedShipping(
        shipping_address_common_pb2.FindByIdShippingRequest(id=shipping_id),
        timeout=5,
    )
    deleted = await command.DeleteShippingPermanent(
        shipping_address_common_pb2.FindByIdShippingRequest(id=shipping_id),
        timeout=5,
    )
    assert deleted.message == "Successfully deleted shipping address permanently"
    await channel.close()


async def test_delete_by_order_permanent_over_grpc(
    db: Database, order_parents, shipping_address_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(shipping_address_grpc_server)
    query = shipping_address_query_pb2_grpc.ShippingQueryServiceStub(channel)
    command = shipping_address_command_pb2_grpc.ShippingCommandServiceStub(channel)
    order_id = await _seed_order(db, order_parents)

    await command.CreateShipping(
        shipping_address_command_pb2.CreateShippingAddressRequest(
            order_id=order_id,
            alamat=_alamat(),
            provinsi="DKI Jakarta",
            kota="Jakarta",
            courier="JNE",
            shipping_method="REG",
            shipping_cost=10000,
            negara="Indonesia",
        ),
        timeout=5,
    )
    deleted = await command.DeleteShippingByOrderPermanent(
        shipping_address_common_pb2.FindByIdShippingRequest(id=order_id),
        timeout=5,
    )
    assert (
        deleted.message
        == "Successfully deleted shipping addresses by order permanently"
    )

    with pytest.raises(grpc.aio.AioRpcError) as missing:
        await query.FindByOrder(
            shipping_address_common_pb2.FindByIdShippingRequest(id=order_id),
            timeout=5,
        )
    assert missing.value.code() is grpc.StatusCode.NOT_FOUND
    await channel.close()


async def test_restore_all_and_delete_all_over_grpc(
    db: Database, order_parents, shipping_address_grpc_server: str
) -> None:
    from google.protobuf import empty_pb2

    channel = grpc.aio.insecure_channel(shipping_address_grpc_server)
    command = shipping_address_command_pb2_grpc.ShippingCommandServiceStub(channel)
    order_id = await _seed_order(db, order_parents)
    alamat = _alamat()

    created = await command.CreateShipping(
        shipping_address_command_pb2.CreateShippingAddressRequest(
            order_id=order_id,
            alamat=alamat,
            provinsi="DKI Jakarta",
            kota="Jakarta",
            courier="JNE",
            shipping_method="REG",
            shipping_cost=10000,
            negara="Indonesia",
        ),
        timeout=5,
    )
    await command.TrashedShipping(
        shipping_address_common_pb2.FindByIdShippingRequest(id=created.data.id),
        timeout=5,
    )

    restored_all = await command.RestoreAllShipping(empty_pb2.Empty(), timeout=5)
    assert restored_all.message == "Successfully restored all shipping addresses"

    await command.TrashedShipping(
        shipping_address_common_pb2.FindByIdShippingRequest(id=created.data.id),
        timeout=5,
    )
    deleted_all = await command.DeleteAllShippingPermanent(
        empty_pb2.Empty(), timeout=5
    )
    assert (
        deleted_all.message
        == "Successfully deleted all shipping addresses permanently"
    )
    await channel.close()
