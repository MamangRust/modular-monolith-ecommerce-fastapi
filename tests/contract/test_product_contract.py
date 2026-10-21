"""Gateway contract tests: FastAPI REST -> real product gRPC over HTTPX.

Marked `integration` because it needs PostgreSQL + Redis (the product service is
real). The product service's command path validates the parent category and
merchant through gRPC adapters, so the `product_grpc_server` fixture also runs
the two `FindById` stubs; the test still seeds the real merchant + category rows
the product FKs require.

Verifies: create returns 201 (`http.StatusCreated`); the REST timestamp shape;
the `deleted_at` wrapper on the trashed list; static paths (`/active`,
`/trashed`, `/restore/all`, `/permanent/all`) winning over the `{product_id}`
variants; the gateway 400 guards (`Invalid Product ID`, `Invalid Merchant ID`,
`Invalid ID`); the 404 `NOT_FOUND` preservation; and the validation 400.
"""

from __future__ import annotations

import uuid

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pkg.database.database import Database
from pkg.logger.logger import get_logger
from pkg.upload_image import new_image_upload
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from service.apigateway.handler.product import handler as product_handler
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration


def _app(server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"product": channel}, addresses={"product": server}
    )
    app.state.upload_image = new_image_upload(get_logger("test-product"))
    register_exception_handlers(app)
    register_routers(app)
    return app


async def _seed(db: Database) -> tuple[int, int, int, str, str]:
    email = f"test_product_contract_{uuid.uuid4().hex[:10]}@example.com"
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
    return user_id, merchant_id, category_id, merchant_name, category_name


async def _cleanup(db: Database, user_id: int, merchant_id: int, category_id: int) -> None:
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


def _create_fields(merchant_id: int, category_id: int, name: str) -> dict[str, object]:
    return {
        "merchant_id": merchant_id,
        "category_id": category_id,
        "name": name,
        "description": "contract test product",
        "price": 1200,
        "count_in_stock": 5,
        "brand": "Samsung",
        "weight": 200,
        "rating": 4,
        "slug_product": f"contract-{uuid.uuid4().hex[:8]}",
    }


async def test_product_rest_contract(
    db: Database, product_grpc_server: str, tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(product_handler, "_UPLOAD_DIR", str(tmp_path / "products"))
    channel = grpc.aio.insecure_channel(product_grpc_server)
    app = _app(product_grpc_server, channel)

    user_id, merchant_id, category_id, _, category_name = await _seed(db)
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            created = await client.post(
                "/api/product-command/create",
                data=_create_fields(merchant_id, category_id, "Galaxy S24 Contract"),
                files={"image": ("prod.png", b"img-bytes", "image/png")},
            )
            assert created.status_code == 201
            body = created.json()
            assert body["status"] == "success"
            assert body["message"] == "Successfully created product"
            assert body["data"]["name"] == "Galaxy S24 Contract"
            assert body["data"]["rating"] == 4.0
            assert len(body["data"]["created_at"]) == 23
            assert body["data"]["image_product"].startswith(str(tmp_path / "products"))
            product_id = body["data"]["id"]

            listed = await client.get(
                "/api/product-query", params={"search": "Galaxy S24 Contract"}
            )
            assert listed.status_code == 200
            assert listed.json()["pagination"]["total_records"] >= 1
            assert listed.json()["data"][0]["id"] == product_id

            by_id = await client.get(f"/api/product-query/{product_id}")
            assert by_id.status_code == 200
            assert by_id.json()["data"]["id"] == product_id

            by_merchant = await client.get(
                f"/api/product-query/merchant/{merchant_id}"
            )
            assert by_merchant.status_code == 200
            assert any(
                r["id"] == product_id for r in by_merchant.json()["data"]
            )

            by_category = await client.get(
                f"/api/product-query/category/{category_name}"
            )
            assert by_category.status_code == 200
            assert any(
                r["id"] == product_id for r in by_category.json()["data"]
            )

            # Static paths win over `/{product_id}`.
            active = await client.get("/api/product-query/active")
            assert active.status_code == 200
            assert active.json()["status"] == "success"

            trashed_list = await client.get("/api/product-query/trashed")
            assert trashed_list.status_code == 200
            assert trashed_list.json()["status"] == "success"

            bad_id = await client.get("/api/product-query/0")
            assert bad_id.status_code == 400
            assert bad_id.json()["message"] == "Invalid Product ID"

            bad_merchant = await client.get("/api/product-query/merchant/0")
            assert bad_merchant.status_code == 400
            assert bad_merchant.json()["message"] == "Invalid Merchant ID"

            missing = await client.get("/api/product-query/2000000000")
            assert missing.status_code == 404
            assert missing.json()["type"] == "NOT_FOUND"

            invalid = await client.post(
                "/api/product-command/create",
                data={
                    **_create_fields(merchant_id, category_id, ""),
                },
            )
            assert invalid.status_code == 400

            updated = await client.post(
                f"/api/product-command/update/{product_id}",
                data={
                    **_create_fields(merchant_id, category_id, "Galaxy S25 Ultra"),
                    "price": 1500,
                    "rating": 5,
                },
                files={"image": ("prod2.png", b"img-bytes", "image/png")},
            )
            assert updated.status_code == 200
            assert updated.json()["data"]["name"] == "Galaxy S25 Ultra"
            assert updated.json()["data"]["rating"] == 5.0

            bad_update = await client.post(
                "/api/product-command/update/0",
                data=_create_fields(merchant_id, category_id, "x"),
            )
            assert bad_update.status_code == 400
            assert bad_update.json()["message"] == "Invalid ID"

            trashed = await client.post(
                f"/api/product-command/trashed/{product_id}"
            )
            assert trashed.status_code == 200
            assert trashed.json()["message"] == "Successfully trashed product"

            trashed_rows = await client.get(
                "/api/product-query/trashed",
                params={"search": "Galaxy S25 Ultra"},
            )
            assert any(
                r["id"] == product_id and r["deleted_at"]
                for r in trashed_rows.json()["data"]
            )

            restored = await client.post(
                f"/api/product-command/restore/{product_id}"
            )
            assert restored.status_code == 200
            assert restored.json()["data"]["id"] == product_id

            # Static path wins over `/restore/{product_id}`.
            restore_all = await client.post("/api/product-command/restore/all")
            assert restore_all.status_code == 200
            assert restore_all.json()["message"] == "Successfully restored all products"

            await client.post(f"/api/product-command/trashed/{product_id}")
            deleted = await client.delete(
                f"/api/product-command/permanent/{product_id}"
            )
            assert deleted.status_code == 200
            assert (
                deleted.json()["message"]
                == "Successfully deleted product permanently"
            )

            permanent_all = await client.post("/api/product-command/permanent/all")
            assert permanent_all.status_code == 200
            assert (
                permanent_all.json()["message"]
                == "Successfully deleted all products permanently"
            )
    finally:
        await channel.close()
        await _cleanup(db, user_id, merchant_id, category_id)


__all__ = []
