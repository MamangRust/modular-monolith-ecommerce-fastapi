"""Gateway contract tests: FastAPI REST -> real cart gRPC over HTTPX.

Marked `integration` because it needs PostgreSQL + Redis (the cart service is
real). The `cart_grpc_server` fixture also runs the real user + product servers
the cart adapters call, so the test seeds the real user + merchant + category +
product rows.

The gateway reads the owner id from the JWT (`request.state.user_id`); the test
app installs a tiny middleware that lifts an `X-User-Id` header into that state,
so the auth path can be exercised without minting a token.

Verifies: create returns 201 (`http.StatusCreated`); the date-only REST
timestamp; the cart listing; the 401 guard when no subject is present; the
gateway/body 400s (`Validation failed`, `Insufficient product stock`); and the
delete/delete-all envelopes.
"""

from __future__ import annotations

import uuid

import grpc
import httpx
import pytest
from fastapi import FastAPI, Request

from pkg.database.database import Database
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration


def _app(server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"cart": channel}, addresses={"cart": server}
    )
    register_exception_handlers(app)
    register_routers(app)

    @app.middleware("http")
    async def _lift_user(request: Request, call_next):
        header = request.headers.get("X-User-Id")
        if header is not None:
            request.state.user_id = int(header)
        return await call_next(request)

    return app


async def _seed(db: Database) -> tuple[int, int, int, int]:
    email = f"test_cart_contract_{uuid.uuid4().hex[:10]}@example.com"
    merchant_name = f"Merchant {uuid.uuid4().hex[:10]}"
    category_name = f"Category {uuid.uuid4().hex[:10]}"
    user = await db.execute(
        """
        INSERT INTO users (firstname, lastname, email, password, verification_code)
        VALUES ('T', 'U', :email, 'x', 'v')
        RETURNING user_id
        """,
        {"email": email},
    )
    assert user is not None
    user_id = int(user["user_id"])
    merchant = await db.execute(
        """
        INSERT INTO merchants (
            user_id, name, description, address, contact_email, contact_phone, status
        )
        VALUES (:user_id, :name, 'd', 'a', 'e@f.com', '0812', 'active')
        RETURNING merchant_id
        """,
        {"user_id": user_id, "name": merchant_name},
    )
    assert merchant is not None
    merchant_id = int(merchant["merchant_id"])
    category = await db.execute(
        """
        INSERT INTO categories (name, description, slug_category, image_category)
        VALUES (:name, 'd', :slug, 'img.jpg')
        RETURNING category_id
        """,
        {"name": category_name, "slug": uuid.uuid4().hex[:10]},
    )
    assert category is not None
    category_id = int(category["category_id"])
    product = await db.execute(
        """
        INSERT INTO products (
            merchant_id, category_id, name, description, price,
            count_in_stock, brand, weight, rating, slug_product, image_product
        )
        VALUES (
            :mid, :cid, :name, 'd', 1200, 5, 'Samsung', 200, 4.5, :slug, 'galaxy-s24.jpg'
        )
        RETURNING product_id
        """,
        {
            "mid": merchant_id,
            "cid": category_id,
            "name": f"Galaxy S24 {uuid.uuid4().hex[:6]}",
            "slug": f"galaxy-{uuid.uuid4().hex[:8]}",
        },
    )
    assert product is not None
    product_id = int(product["product_id"])
    return user_id, product_id, merchant_id, category_id


async def _cleanup(db: Database, user_id: int, merchant_id: int, category_id: int) -> None:
    await db.execute("DELETE FROM carts WHERE user_id = :uid", {"uid": user_id})
    await db.execute(
        "DELETE FROM products WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute(
        "DELETE FROM categories WHERE category_id = :cid", {"cid": category_id}
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


async def test_cart_rest_contract(db: Database, cart_grpc_server: str) -> None:
    channel = grpc.aio.insecure_channel(cart_grpc_server)
    app = _app(cart_grpc_server, channel)

    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            headers = {"X-User-Id": str(user_id)}

            # Missing subject -> 401.
            unauth = await client.get("/api/cart-query")
            assert unauth.status_code == 401

            created = await client.post(
                "/api/cart-command/create",
                json={"product_id": product_id, "quantity": 2},
                headers=headers,
            )
            assert created.status_code == 201
            body = created.json()
            assert body["status"] == "success"
            assert body["message"] == "Successfully created cart"
            assert body["data"]["product_id"] == product_id
            assert body["data"]["user_id"] == user_id
            assert body["data"]["price"] == 1200
            assert body["data"]["image"] == "galaxy-s24.jpg"
            assert len(body["data"]["created_at"]) == 10
            cart_id = body["data"]["id"]

            listed = await client.get(
                "/api/cart-query", params={"page": 1, "page_size": 10}, headers=headers
            )
            assert listed.status_code == 200
            assert listed.json()["pagination"]["total_records"] >= 1
            assert any(r["id"] == cart_id for r in listed.json()["data"])

            # Body validation 400 (quantity must be >= 1).
            invalid = await client.post(
                "/api/cart-command/create",
                json={"product_id": product_id, "quantity": 0},
                headers=headers,
            )
            assert invalid.status_code == 400
            assert invalid.json()["message"] == "Validation failed"

            # Stock guard 400.
            over_stock = await client.post(
                "/api/cart-command/create",
                json={"product_id": product_id, "quantity": 6},
                headers=headers,
            )
            assert over_stock.status_code == 400
            assert over_stock.json()["message"] == "Insufficient product stock"

            deleted = await client.request(
                "DELETE",
                "/api/cart-command/delete",
                json={"cart_id": cart_id, "user_id": user_id},
                headers=headers,
            )
            assert deleted.status_code == 200
            assert deleted.json()["message"] == "Successfully deleted cart item permanently"

            first = await client.post(
                "/api/cart-command/create",
                json={"product_id": product_id, "quantity": 1},
                headers=headers,
            )
            second = await client.post(
                "/api/cart-command/create",
                json={"product_id": product_id, "quantity": 1},
                headers=headers,
            )
            deleted_all = await client.post(
                "/api/cart-command/delete-all",
                json={
                    "user_id": user_id,
                    "cart_ids": [first.json()["data"]["id"], second.json()["data"]["id"]],
                },
                headers=headers,
            )
            assert deleted_all.status_code == 200
            assert (
                deleted_all.json()["message"]
                == "Successfully deleted all cart items permanently"
            )
    finally:
        await channel.close()
        await _cleanup(db, user_id, merchant_id, category_id)


__all__ = []
