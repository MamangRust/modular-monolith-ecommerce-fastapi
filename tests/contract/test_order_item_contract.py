"""Gateway contract tests: FastAPI REST -> real order_item gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the order_item service is real, not mocked). The order-item routes are JWT-only (no `RequireRoles` middleware in the reference), so the test app registers the routers directly without an auth layer. `Create`/`Update` are not exposed as REST routes (the gateway wires them as internal gRPC only), so the fixture seeds an item through the generated command stub directly. `order_items` carries FKs to `orders` and `products`, so the test uses the `order_parents` fixture."""

from __future__ import annotations

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pb.order_item import (
    order_item_command_pb2,
    order_item_command_pb2_grpc,
)
from pkg.database.database import Database
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration


def _app(order_item_grpc_server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"order_item": channel},
        addresses={"order_item": order_item_grpc_server},
    )
    register_exception_handlers(app)
    register_routers(app)
    return app


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


async def test_order_item_rest_contract(
    db: Database, order_parents, order_item_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(order_item_grpc_server)
    command = order_item_command_pb2_grpc.OrderItemCommandServiceStub(channel)
    app = _app(order_item_grpc_server, channel)
    order_id = await _seed_order(db, order_parents)
    product_id = order_parents.product_id
    transport = httpx.ASGITransport(app=app)

    created = await command.CreateOrderItem(
        order_item_command_pb2.CreateOrderItemRecordRequest(
            order_id=order_id, product_id=product_id, quantity=2, price=5000
        ),
        timeout=5,
    )
    item_id = created.data.id
    assert item_id > 0

    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        listed = await client.get(
            "/api/order-item", params={"search": str(product_id)}
        )
        assert listed.status_code == 200
        listed_body = listed.json()
        assert listed_body["pagination"]["total_records"] >= 1
        assert listed_body["data"][0]["id"] == item_id
        assert listed_body["data"][0]["order_id"] == order_id

        active = await client.get(
            "/api/order-item/active", params={"search": str(product_id)}
        )
        assert active.status_code == 200
        assert active.json()["status"] == "success"

        trashed_list = await client.get(
            "/api/order-item/trashed", params={"search": str(product_id)}
        )
        assert trashed_list.status_code == 200
        assert trashed_list.json()["status"] == "success"

        by_order = await client.get(f"/api/order-item/order/{order_id}")
        assert by_order.status_code == 200
        assert any(row["id"] == item_id for row in by_order.json()["data"])

        bad_order = await client.get("/api/order-item/order/0")
        assert bad_order.status_code == 400
        assert bad_order.json()["message"] == "Invalid Order ID"

        bad_id = await client.post("/api/order-item/trash/0")
        assert bad_id.status_code == 400
        assert bad_id.json()["message"] == "Invalid ID"

        missing = await client.post("/api/order-item/trash/2000000000")
        assert missing.status_code == 404
        assert missing.json()["type"] == "NOT_FOUND"

        trashed = await client.post(f"/api/order-item/trash/{item_id}")
        assert trashed.status_code == 200
        assert trashed.json()["message"] == "Successfully trashed order item"

        # FindAll filters `deleted_at IS NULL`.
        after_trash = await client.get(
            "/api/order-item", params={"search": str(product_id)}
        )
        assert all(row["id"] != item_id for row in after_trash.json()["data"])

        in_trash = await client.get(
            "/api/order-item/trashed", params={"search": str(product_id)}
        )
        assert any(row["id"] == item_id for row in in_trash.json()["data"])

        restored = await client.post(f"/api/order-item/restore/{item_id}")
        assert restored.status_code == 200
        assert restored.json()["data"]["id"] == item_id

        # Static path must win over `/restore/{order_item_id}`.
        restore_all = await client.post("/api/order-item/restore/all")
        assert restore_all.status_code == 200
        assert (
            restore_all.json()["message"]
            == "Successfully restored all order items"
        )

        await client.post(f"/api/order-item/trash/{item_id}")
        deleted = await client.delete(f"/api/order-item/permanent/{item_id}")
        assert deleted.status_code == 200
        assert (
            deleted.json()["message"]
            == "Successfully deleted order item permanently"
        )

        permanent_all = await client.post("/api/order-item/permanent/all")
        assert permanent_all.status_code == 200
        assert (
            permanent_all.json()["message"]
            == "Successfully deleted all order items permanently"
        )
    await channel.close()
