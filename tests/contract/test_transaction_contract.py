"""Gateway contract tests: FastAPI REST -> real transaction gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the transaction service is real). The `transaction_grpc_server` fixture also runs the real user/merchant/order/order_item/shipping servers the saga resolves, so `POST /create` performs the full remote derivation. Verifies: create returns **201** (`http.StatusCreated` — unlike order which uses 200); the derived amount (items + shipping + 11% PPN); the seconds REST timestamps; the always-emitted `deleted_at` key (`""` when active); the query path guards ("Invalid Transaction ID" / "Invalid Merchant ID" — 400); the command "Invalid ID" guards; `update` reading `status` from the query string (`FormValue`); and the stats routes (global + by-merchant with the `merchant_id` query param)."""

from __future__ import annotations

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pkg.database.database import Database
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration

DERIVED_TOTAL = 12765  # 2 * 5000 + 1500 shipping, + 11% PPN


class Family:
    def __init__(self, user_id: int, merchant_id: int, order_id: int) -> None:
        self.user_id = user_id
        self.merchant_id = merchant_id
        self.order_id = order_id


@pytest.fixture
async def family(db: Database, order_parents):
    """order + item + shipping rows the transaction saga can resolve."""
    order = await db.execute(
        """
        INSERT INTO orders (user_id, merchant_id, total_price)
        VALUES (:user_id, :merchant_id, :total_price)
        RETURNING order_id
        """,
        {
            "user_id": order_parents.user_id,
            "merchant_id": order_parents.merchant_id,
            "total_price": 11500,
        },
    )
    assert order is not None
    order_id = int(order["order_id"])
    await db.execute(
        """
        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (:order_id, :product_id, 2, 5000)
        """,
        {"order_id": order_id, "product_id": order_parents.product_id},
    )
    await db.execute(
        """
        INSERT INTO shipping_addresses (
            order_id, alamat, provinsi, kota, courier, shipping_method,
            shipping_cost, negara
        )
        VALUES (:order_id, 'Jalan Panjang', 'DKI', 'Jakarta', 'jne', 'reg',
                1500, 'Indonesia')
        """,
        {"order_id": order_id},
    )
    return Family(order_parents.user_id, order_parents.merchant_id, order_id)


def _app(server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"transaction": channel}, addresses={"transaction": server}
    )
    register_exception_handlers(app)
    register_routers(app)
    return app


async def test_transaction_rest_contract(
    db: Database, family, transaction_grpc_server
) -> None:
    channel = grpc.aio.insecure_channel(transaction_grpc_server)
    app = _app(transaction_grpc_server, channel)
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            # ---- create: 201 + derived amount
            created = await client.post(
                "/api/transaction-command/create",
                json={
                    "order_id": family.order_id,
                    "merchant_id": family.merchant_id,
                    "payment_method": "credit_card",
                    "amount": DERIVED_TOTAL,
                    "user_id": family.user_id,
                    "payment_status": "",
                },
            )
            assert created.status_code == 201  # transaction create uses 201
            body = created.json()
            assert body["status"] == "success"
            assert body["message"] == "Successfully created transaction"
            assert body["data"]["amount"] == DERIVED_TOTAL
            assert body["data"]["payment_status"] == "success"
            assert len(body["data"]["created_at"]) == 19  # seconds layout
            transaction_id = body["data"]["id"]

            # ---- query surface
            listed = await client.get("/api/transaction-query?page=1&page_size=5")
            assert listed.status_code == 200
            assert listed.json()["pagination"]["total_records"] >= 1

            got = await client.get(f"/api/transaction-query/{transaction_id}")
            assert got.status_code == 200
            assert got.json()["data"]["id"] == transaction_id

            bad_id = await client.get("/api/transaction-query/0")
            assert bad_id.status_code == 400
            assert bad_id.json()["message"] == "Invalid Transaction ID"

            bad_merchant = await client.get(
                "/api/transaction-query/merchant/0"
            )
            assert bad_merchant.status_code == 400
            assert bad_merchant.json()["message"] == "Invalid Merchant ID"

            ok_merchant = await client.get(
                f"/api/transaction-query/merchant/{family.merchant_id}"
            )
            assert ok_merchant.status_code == 200

            active = await client.get("/api/transaction-query/active")
            assert active.status_code == 200

            # update: status from the query string (FormValue)
            updated = await client.post(
                f"/api/transaction-command/update/{transaction_id}?status=refunded"
            )
            assert updated.status_code == 200
            assert updated.json()["data"]["payment_status"] == "refunded"

            bad_update = await client.post("/api/transaction-command/update/0")
            assert bad_update.status_code == 400
            assert bad_update.json()["message"] == "Invalid ID"

            # ---- trash -> trashed listing -> restore -> permanent delete
            trashed = await client.post(
                f"/api/transaction-command/trashed/{transaction_id}"
            )
            assert trashed.status_code == 200
            assert trashed.json()["data"]["deleted_at"] != ""

            trashed_list = await client.get("/api/transaction-query/trashed")
            assert trashed_list.status_code == 200

            restored = await client.post(
                f"/api/transaction-command/restore/{transaction_id}"
            )
            assert restored.status_code == 200
            assert restored.json()["data"]["deleted_at"] == ""

            all_restored = await client.post(
                "/api/transaction-command/restore/all"
            )
            assert all_restored.status_code == 200

            deleted = await client.delete(
                f"/api/transaction-command/permanent/{transaction_id}"
            )
            assert deleted.status_code == 200
            assert (
                deleted.json()["message"]
                == "Successfully deleted transaction permanently"
            )

            all_deleted = await client.post(
                "/api/transaction-command/permanent/all"
            )
            assert all_deleted.status_code == 200

            # ---- stats: global + by-merchant (merchant_id from the query)
            stats = await client.get(
                "/api/transaction-stats/yearly-success?year=2026"
            )
            assert stats.status_code == 200
            assert stats.json()["message"] == (
                "Successfully fetched yearly amount success stats"
            )

            month = await client.get(
                "/api/transaction-stats/monthly-success?year=2026&month=1"
            )
            assert month.status_code == 200

            by_merchant = await client.get(
                "/api/transaction-stats/merchant/yearly-success"
                f"?year=2026&merchant_id={family.merchant_id}"
            )
            assert by_merchant.status_code == 200
            assert by_merchant.json()["message"] == (
                "Successfully fetched yearly amount success stats by merchant"
            )

            method = await client.get(
                "/api/transaction-stats/monthly-method-success?year=2026&month=1"
            )
            assert method.status_code == 200

            # The final delete only matches trashed rows and this row was
            # active, so purge it explicitly (test-scoped cleanup).
            await db.execute(
                "DELETE FROM transactions WHERE order_id = :oid",
                {"oid": family.order_id},
            )
    finally:
        await channel.close()
