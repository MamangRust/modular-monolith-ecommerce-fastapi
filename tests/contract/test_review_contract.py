"""Gateway contract tests: FastAPI REST -> real review gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the review service is real). The `review_grpc_server` fixture also runs the real user + product servers the review adapters call, so the test seeds the real user + merchant + category + product rows. The gateway reads the author id from the JWT (`request.state.user_id`); the test app installs a tiny middleware that lifts an `X-User-Id` header into that state, so the auth path can be exercised without minting a token. Only `Create` reads the subject (the review groups carry no auth middleware), so a missing header is a 401 only on `POST /create`."""

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
        channels={"review": channel}, addresses={"review": server}
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
    email = f"test_review_contract_{uuid.uuid4().hex[:10]}@example.com"
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
        {"user_id": user_id, "name": f"Merchant {uuid.uuid4().hex[:10]}"},
    )
    assert merchant is not None
    merchant_id = int(merchant["merchant_id"])
    category = await db.execute(
        """
        INSERT INTO categories (name, description, slug_category, image_category)
        VALUES (:name, 'd', :slug, 'img.jpg')
        RETURNING category_id
        """,
        {"name": f"Category {uuid.uuid4().hex[:10]}", "slug": uuid.uuid4().hex[:10]},
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
    return user_id, int(product["product_id"]), merchant_id, category_id


async def _cleanup(db: Database, user_id: int, merchant_id: int, category_id: int) -> None:
    await db.execute("DELETE FROM reviews WHERE user_id = :uid", {"uid": user_id})
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


async def test_review_rest_contract(db: Database, review_grpc_server: str) -> None:
    channel = grpc.aio.insecure_channel(review_grpc_server)
    app = _app(review_grpc_server, channel)

    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            headers = {"X-User-Id": str(user_id)}

            # Missing subject -> 401 (only Create reads the JWT subject).
            unauth = await client.post(
                "/api/review-command/create",
                json={"product_id": product_id, "rating": 5, "comment": "x"},
            )
            assert unauth.status_code == 401
            assert unauth.json()["message"] == "Unauthorized"

            # The body's user_id is ignored; the JWT subject wins.
            created = await client.post(
                "/api/review-command/create",
                json={
                    "user_id": 999_999,
                    "product_id": product_id,
                    "rating": 5,
                    "comment": "Produk bagus!",
                },
                headers=headers,
            )
            assert created.status_code == 201
            body = created.json()
            assert body["status"] == "success"
            assert body["message"] == "Successfully created review"
            assert body["data"]["user_id"] == user_id
            assert body["data"]["product_id"] == product_id
            assert body["data"]["comment"] == "Produk bagus!"
            assert body["data"]["rating"] == 5
            assert body["data"]["name"] == ""  # request carries no name
            assert len(body["data"]["created_at"]) == 10  # date-only
            review_id = body["data"]["id"]

            # A second review stays active so `/active` is guaranteed non-empty
            # after the first is trashed (the real DB may have no other reviews).
            keeper = await client.post(
                "/api/review-command/create",
                json={"product_id": product_id, "rating": 3, "comment": "keeper"},
                headers=headers,
            )
            keeper_id = keeper.json()["data"]["id"]

            listed = await client.get(
                "/api/review-query", params={"page": 1, "page_size": 10}
            )
            assert listed.status_code == 200
            assert listed.json()["message"] == "Successfully fetched reviews"
            assert listed.json()["pagination"]["total_records"] >= 1
            assert any(r["id"] == review_id for r in listed.json()["data"])

            by_product = await client.get(
                f"/api/review-query/product/{product_id}",
                params={"page": 1, "page_size": 10},
            )
            assert by_product.status_code == 200
            assert by_product.json()["message"] == "Successfully fetched product reviews"
            # drops the pagination block on the detail mappers -> all zeros.
            assert by_product.json()["pagination"] == {
                "current_page": 0,
                "page_size": 0,
                "total_pages": 0,
                "total_records": 0,
            }
            # Detail rows use the .mmm timestamp layout.
            assert len(by_product.json()["data"][0]["created_at"]) == 23

            by_merchant = await client.get(
                f"/api/review-query/merchant/{merchant_id}",
                params={"page": 1, "page_size": 10},
            )
            assert by_merchant.status_code == 200
            assert (
                by_merchant.json()["message"]
                == "Successfully fetched merchant reviews"
            )
            assert any(r["id"] == review_id for r in by_merchant.json()["data"])

            updated = await client.post(
                f"/api/review-command/update/{review_id}",
                json={"rating": 4, "comment": "updated"},
                headers=headers,
            )
            assert updated.status_code == 200
            assert updated.json()["message"] == "Successfully updated review"
            assert updated.json()["data"]["comment"] == "updated"
            assert updated.json()["data"]["rating"] == 4

            # Body validation 400 (rating/comment required).
            invalid = await client.post(
                f"/api/review-command/update/{review_id}",
                json={"rating": 0, "comment": ""},
                headers=headers,
            )
            assert invalid.status_code == 400
            assert invalid.json()["message"] == "Validation failed"

            trashed = await client.post(
                f"/api/review-command/trashed/{review_id}", headers=headers
            )
            assert trashed.status_code == 200
            assert trashed.json()["message"] == "Successfully trashed review"
            assert len(trashed.json()["data"]["deleted_at"]) == 10  # date-only

            active = await client.get(
                "/api/review-query/active", params={"page": 1, "page_size": 100}
            )
            assert active.status_code == 200
            assert active.json()["message"] == "Successfully fetched active reviews"
            assert all(r["id"] != review_id for r in active.json()["data"])
            # Active rows still carry the (empty) deleted_at field.
            assert any(r["id"] == keeper_id for r in active.json()["data"])
            assert active.json()["data"][0]["deleted_at"] == ""

            trashed_rows = await client.get(
                "/api/review-query/trashed", params={"page": 1, "page_size": 100}
            )
            assert trashed_rows.status_code == 200
            assert trashed_rows.json()["message"] == "Successfully fetched trashed reviews"
            assert any(r["id"] == review_id for r in trashed_rows.json()["data"])

            # Global restore (the route takes no body): restores trashed rows.
            restored_all = await client.post(
                "/api/review-command/restore/all", headers=headers
            )
            assert restored_all.status_code == 200
            assert restored_all.json()["message"] == "Successfully restored all reviews"

            # Single-row permanent delete requires a trashed row.
            await client.post(f"/api/review-command/trashed/{review_id}", headers=headers)
            deleted = await client.request(
                "DELETE",
                f"/api/review-command/permanent/{review_id}",
                headers=headers,
            )
            assert deleted.status_code == 200
            assert deleted.json()["message"] == "Successfully deleted review permanently"

            # Bulk permanent delete (global): trash the keeper first.
            await client.post(
                f"/api/review-command/trashed/{keeper_id}", headers=headers
            )
            deleted_all = await client.post(
                "/api/review-command/permanent/all", headers=headers
            )
            assert deleted_all.status_code == 200
            assert (
                deleted_all.json()["message"]
                == "Successfully deleted all reviews permanently"
            )
    finally:
        await channel.close()
        await _cleanup(db, user_id, merchant_id, category_id)


__all__ = []
