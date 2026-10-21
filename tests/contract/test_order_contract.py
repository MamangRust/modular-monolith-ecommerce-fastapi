"""Gateway contract tests: FastAPI REST -> real order gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the order service is real). The `order_grpc_server` fixture also runs the real product/order_item/ shipping servers the order adapters call, so the create saga reserves stock, writes order items and creates the shipping address for real; the test seeds the real FK parents via `order_parents`. The order gateway reads `merchant_id`/`user_id` from the **body** (binds the whole request), so `POST /create` needs no JWT subject — unlike review. The gateway keeps no cache. Verifies: create returns 200 (the whole order command surface uses `http.StatusOK`, not review's 201); the millisecond REST timestamps; the always-emitted `deleted_at` key on delete-at rows (`""` when active); the body 400 (`Validation failed`); the trash/restore/permanent envelopes; and the eight stats routes incl. the verbatim guard inconsistencies (400 with the domain message)."""

from __future__ import annotations

from datetime import datetime

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pkg.database.database import Database
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration


def _app(server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"order": channel}, addresses={"order": server}
    )
    register_exception_handlers(app)
    register_routers(app)
    return app


def _create_body(parents, *, quantity: int = 2) -> dict:
    return {
        "merchant_id": parents.merchant_id,
        "user_id": parents.user_id,
        "total_price": 1,
        "items": [
            {"product_id": parents.product_id, "quantity": quantity, "price": 5000}
        ],
        "shipping_address": {
            "alamat": "Jalan Panjang No 1",
            "provinsi": "DKI Jakarta",
            "kota": "Jakarta",
            "courier": "jne",
            "shipping_method": "reg",
            "shipping_cost": 15000,
            "negara": "Indonesia",
        },
    }


async def test_order_rest_contract(db: Database, order_parents, order_grpc_server) -> None:
    channel = grpc.aio.insecure_channel(order_grpc_server)
    app = _app(order_grpc_server, channel)
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            created = await client.post(
                "/api/order-command/create", json=_create_body(order_parents)
            )
            assert created.status_code == 200  # not 201 (order uses StatusOK)
            body = created.json()
            assert body["status"] == "success"
            assert body["message"] == "Successfully created order"
            assert body["data"]["merchant_id"] == order_parents.merchant_id
            assert body["data"]["user_id"] == order_parents.user_id
            assert body["data"]["total_price"] == 25000  # 2 * 5000 + 15000
            assert len(body["data"]["created_at"]) == 23  # .mmm layout
            order_id = body["data"]["id"]

            listed = await client.get(
                "/api/order-query",
                params={"page": 1, "page_size": 10, "search": str(order_id)},
            )
            assert listed.status_code == 200
            assert listed.json()["message"] == "Successfully fetched order"
            assert listed.json()["pagination"]["total_records"] >= 1
            assert any(r["id"] == order_id for r in listed.json()["data"])

            by_id = await client.get(f"/api/order-query/{order_id}")
            assert by_id.status_code == 200
            assert by_id.json()["message"] == "Successfully fetched order"
            assert by_id.json()["data"]["id"] == order_id

            # The item id is needed for the update; read it from the DB.
            item = await db.scalar(
                """
                SELECT order_item_id FROM order_items
                WHERE order_id = :order_id AND deleted_at IS NULL
                """,
                {"order_id": order_id},
            )
            assert item is not None
            order_item_id = int(item["order_item_id"])

            updated = await client.post(
                f"/api/order-command/update/{order_id}",
                json={
                    "user_id": order_parents.user_id,
                    "total_price": 1,
                    "items": [
                        {
                            "order_item_id": order_item_id,
                            "product_id": order_parents.product_id,
                            "quantity": 3,
                            "price": 5000,
                        }
                    ],
                },
            )
            assert updated.status_code == 200
            assert updated.json()["message"] == "Successfully updated order"
            assert updated.json()["data"]["total_price"] == 3 * 5000 + 15000

            active = await client.get(
                "/api/order-query/active", params={"page": 1, "page_size": 100}
            )
            assert active.status_code == 200
            assert active.json()["message"] == "Successfully fetched active order"
            active_row = next(r for r in active.json()["data"] if r["id"] == order_id)
            assert active_row["deleted_at"] == ""  # always emitted, empty when active

            # Body validation -> global 400 envelope (not FastAPI's 422).
            invalid = await client.post(
                "/api/order-command/create",
                json={"merchant_id": 1, "user_id": 1, "total_price": 0, "items": []},
            )
            assert invalid.status_code == 400
            assert invalid.json()["message"] == "Validation failed"

            trashed = await client.post(f"/api/order-command/trashed/{order_id}")
            assert trashed.status_code == 200
            assert trashed.json()["message"] == "Successfully trashed order"
            assert trashed.json()["data"]["deleted_at"]  # non-empty on trash

            trashed_rows = await client.get(
                "/api/order-query/trashed", params={"page": 1, "page_size": 100}
            )
            assert trashed_rows.status_code == 200
            assert trashed_rows.json()["message"] == "Successfully fetched trashed order"
            assert any(r["id"] == order_id for r in trashed_rows.json()["data"])

            restored = await client.post(f"/api/order-command/restore/{order_id}")
            assert restored.status_code == 200
            assert restored.json()["message"] == "Successfully restored order"

            await client.post(f"/api/order-command/trashed/{order_id}")
            deleted = await client.request(
                "DELETE", f"/api/order-command/permanent/{order_id}"
            )
            assert deleted.status_code == 200
            assert deleted.json()["message"] == "Successfully deleted order permanently"

            restored_all = await client.post("/api/order-command/restore/all")
            assert restored_all.status_code == 200
            assert restored_all.json()["message"] == "Successfully restored all orders"

            deleted_all = await client.post("/api/order-command/permanent/all")
            assert deleted_all.status_code == 200
            assert (
                deleted_all.json()["message"]
                == "Successfully deleted all orders permanently"
            )
    finally:
        await channel.close()


async def test_order_stats_rest_contract(
    db: Database, order_parents, order_grpc_server
) -> None:
    channel = grpc.aio.insecure_channel(order_grpc_server)
    app = _app(order_grpc_server, channel)
    merchant_id = order_parents.merchant_id
    try:
        order = await db.execute(
            """
            INSERT INTO orders (user_id, merchant_id, total_price, created_at)
            VALUES (:user_id, :merchant_id, 9000, :created_at)
            RETURNING order_id
            """,
            {
                "user_id": order_parents.user_id,
                "merchant_id": merchant_id,
                "created_at": datetime(2001, 7, 10, 9, 0),
            },
        )
        assert order is not None
        order_id = int(order["order_id"])
        await db.execute(
            """
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (:order_id, :product_id, 3, 3000)
            """,
            {"order_id": order_id, "product_id": order_parents.product_id},
        )

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            monthly = await client.get(
                "/api/order/monthly-total-revenue", params={"year": 2001, "month": 7}
            )
            assert monthly.status_code == 200
            assert monthly.json()["message"] == "Monthly sales retrieved successfully"
            july = next(r for r in monthly.json()["data"] if r["month"] == "July")
            assert july["total_revenue"] == 9000

            yearly = await client.get(
                "/api/order/yearly-total-revenue", params={"year": 2001}
            )
            assert yearly.status_code == 200
            assert (
                yearly.json()["message"]
                == "Yearly payment methods retrieved successfully"
            )

            monthly_revenue = await client.get(
                "/api/order/monthly-revenue", params={"year": 2001}
            )
            assert monthly_revenue.status_code == 200
            assert monthly_revenue.json()["message"] == "Monthly revenue data retrieved"

            yearly_revenue = await client.get(
                "/api/order/yearly-revenue", params={"year": 2001}
            )
            assert yearly_revenue.status_code == 200
            assert yearly_revenue.json()["message"] == "Yearly revenue data retrieved"

            bm_monthly = await client.get(
                "/api/order/merchant/monthly-total-revenue",
                params={"year": 2001, "month": 7, "merchant_id": merchant_id},
            )
            assert bm_monthly.status_code == 200
            assert bm_monthly.json()["message"] == "Monthly sales retrieved successfully"

            bm_yearly = await client.get(
                "/api/order/merchant/yearly-total-revenue",
                params={"year": 2001, "merchant_id": merchant_id},
            )
            assert bm_yearly.status_code == 200

            bm_monthly_revenue = await client.get(
                "/api/order/merchant/monthly-revenue",
                params={"year": 2001, "merchant_id": merchant_id},
            )
            assert bm_monthly_revenue.status_code == 200
            assert (
                bm_monthly_revenue.json()["message"]
                == "Monthly revenue by merchant data retrieved"
            )

            bm_yearly_revenue = await client.get(
                "/api/order/merchant/yearly-revenue",
                params={"year": 2001, "merchant_id": merchant_id},
            )
            assert bm_yearly_revenue.status_code == 200
            assert (
                bm_yearly_revenue.json()["message"]
                == "Yearly revenue by merchant data retrieved"
            )

            # Guard inconsistencies surface as 400 with the domain message.
            bad_year = await client.get("/api/order/monthly-total-revenue")
            assert bad_year.status_code == 400
            assert bad_year.json()["message"] == "Invalid year"

            bad_month = await client.get(
                "/api/order/monthly-total-revenue", params={"year": 2001, "month": 13}
            )
            assert bad_month.status_code == 400
            assert bad_month.json()["message"] == "Invalid month"

            # Order-summary RPCs report a bad year with the invalid-id sentinel.
            summary_year = await client.get("/api/order/monthly-revenue")
            assert summary_year.status_code == 400
            assert summary_year.json()["message"] == "Invalid ID"

            bad_merchant = await client.get(
                "/api/order/merchant/monthly-revenue",
                params={"year": 2001, "merchant_id": 0},
            )
            assert bad_merchant.status_code == 400
            assert bad_merchant.json()["message"] == "Invalid merchant ID"

            bad_merchant_yearly = await client.get(
                "/api/order/merchant/yearly-revenue",
                params={"year": 2001, "merchant_id": 0},
            )
            assert bad_merchant_yearly.status_code == 400
            assert bad_merchant_yearly.json()["message"] == "Invalid ID"
    finally:
        await channel.close()


__all__ = []
