"""Gateway contract tests: FastAPI REST -> real shipping_address gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the shipping_address service is real, not mocked). The shipping-address routes are JWT-only (no `RequireRoles` middleware in the reference), so the test app registers the routers directly without an auth layer."""

from __future__ import annotations

import uuid

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pb.shipping_address import (
    shipping_address_command_pb2,
    shipping_address_command_pb2_grpc,
)
from pkg.database.database import Database
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration


def _app(shipping_address_grpc_server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"shipping_address": channel},
        addresses={"shipping_address": shipping_address_grpc_server},
    )
    register_exception_handlers(app)
    register_routers(app)
    return app


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


async def test_shipping_address_rest_contract(
    db: Database, order_parents, shipping_address_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(shipping_address_grpc_server)
    command = shipping_address_command_pb2_grpc.ShippingCommandServiceStub(channel)
    app = _app(shipping_address_grpc_server, channel)
    order_id = await _seed_order(db, order_parents)
    alamat = _alamat()
    transport = httpx.ASGITransport(app=app)

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
    shipping_id = created.data.id
    assert shipping_id > 0

    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        listed = await client.get(
            "/api/shipping-address-query", params={"search": alamat}
        )
        assert listed.status_code == 200
        listed_body = listed.json()
        assert listed_body["pagination"]["total_records"] >= 1
        row = listed_body["data"][0]
        assert row["id"] == shipping_id
        assert row["order_id"] == order_id
        assert row["shipping_cost"] == 12000
        # The REST shape drops courier.
        assert "courier" not in row

        by_id = await client.get(f"/api/shipping-address-query/{shipping_id}")
        assert by_id.status_code == 200
        assert by_id.json()["data"]["id"] == shipping_id

        active = await client.get(
            "/api/shipping-address-query/active", params={"search": alamat}
        )
        assert active.status_code == 200
        assert active.json()["status"] == "success"

        trashed_list = await client.get(
            "/api/shipping-address-query/trashed", params={"search": alamat}
        )
        assert trashed_list.status_code == 200
        assert trashed_list.json()["status"] == "success"

        by_order = await client.get(
            f"/api/shipping-address-query/order/{order_id}"
        )
        assert by_order.status_code == 200
        assert by_order.json()["data"]["id"] == shipping_id

        # Static `/active` must win over `/{shipping_id}`.
        assert active.json()["message"] == "Successfully fetched active shipping addresses"

        bad_order = await client.get("/api/shipping-address-query/order/0")
        assert bad_order.status_code == 400
        assert bad_order.json()["message"] == "Invalid ID"

        bad_id = await client.get("/api/shipping-address-query/0")
        assert bad_id.status_code == 400
        assert bad_id.json()["message"] == "Invalid ID"

        bad_trash = await client.post("/api/shipping-address-command/trashed/0")
        assert bad_trash.status_code == 400
        assert bad_trash.json()["message"] == "Invalid ID"

        missing = await client.post(
            "/api/shipping-address-command/trashed/2000000000"
        )
        assert missing.status_code == 404
        assert missing.json()["type"] == "NOT_FOUND"

        trashed = await client.post(
            f"/api/shipping-address-command/trashed/{shipping_id}"
        )
        assert trashed.status_code == 200
        assert trashed.json()["message"] == "Successfully trashed shipping address"
        assert trashed.json()["data"]["deleted_at"]

        # FindAll filters `deleted_at IS NULL`.
        after_trash = await client.get(
            "/api/shipping-address-query", params={"search": alamat}
        )
        assert all(r["id"] != shipping_id for r in after_trash.json()["data"])

        in_trash = await client.get(
            "/api/shipping-address-query/trashed", params={"search": alamat}
        )
        assert any(r["id"] == shipping_id for r in in_trash.json()["data"])

        restored = await client.post(
            f"/api/shipping-address-command/restore/{shipping_id}"
        )
        assert restored.status_code == 200
        assert restored.json()["data"]["id"] == shipping_id

        # Static path must win over `/restore/{shipping_id}`.
        restore_all = await client.post(
            "/api/shipping-address-command/restore/all"
        )
        assert restore_all.status_code == 200
        assert (
            restore_all.json()["message"]
            == "Successfully restored all shipping addresses"
        )

        await client.post(
            f"/api/shipping-address-command/trashed/{shipping_id}"
        )
        deleted = await client.delete(
            f"/api/shipping-address-command/permanent/{shipping_id}"
        )
        assert deleted.status_code == 200
        assert (
            deleted.json()["message"]
            == "Successfully deleted shipping address permanently"
        )

        permanent_all = await client.post(
            "/api/shipping-address-command/permanent/all"
        )
        assert permanent_all.status_code == 200
        assert (
            permanent_all.json()["message"]
            == "Successfully deleted all shipping addresses permanently"
        )
    await channel.close()
