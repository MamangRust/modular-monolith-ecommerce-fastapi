"""Gateway contract tests: FastAPI REST -> real review_detail gRPC over HTTPX. Marked `integration` because it needs PostgreSQL + Redis (the review_detail service is real, not mocked). Review_detail's `Create`/`Update` ARE exposed as REST (unlike shipping_address), so the fixture seeds through the REST layer. They are multipart endpoints; `url` is accepted either as an uploaded file or as a plain string, matching /. Verifies the REST contract: `id` REST field, date-only timestamps, the static paths (`/active`, `/trashed`, `/restore/all`, `/permanent/all`) winning over the `{review_detail_id}` variants, the 400 `Invalid ID` mapper for command ids, and the 404 `NOT_FOUND` preservation for a missing review detail. Two differences from the slider contract are asserted explicitly: - `FindAll` does NOT filter `deleted_at`, so a trashed review detail still appears in the list endpoint (only `find_active`/`find_by_id` exclude it). - The gRPC `FindById` handler guards `id <= 0` with 400 `invalid ID`, so `/api/review-detail-query/0` returns 400 (the gateway forwards it)."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

import grpc
import httpx
import pytest
from fastapi import FastAPI

from pkg.database.database import Database
from pkg.logger.logger import get_logger
from pkg.upload_image import new_image_upload
from service.apigateway.app.client import ServiceConnections
from service.apigateway.handler import register_routers
from service.apigateway.handler.review_detail import handler as review_detail_handler
from shared.errorhandler import register_exception_handlers

pytestmark = pytest.mark.integration


def _app(review_detail_grpc_server: str, channel: grpc.aio.Channel) -> FastAPI:
    app = FastAPI()
    app.state.connections = ServiceConnections(
        channels={"review_detail": channel},
        addresses={"review_detail": review_detail_grpc_server},
    )
    app.state.upload_image = new_image_upload(get_logger("test-review-detail"))
    register_exception_handlers(app)
    register_routers(app)
    return app


def _caption() -> str:
    return f"Caption {uuid.uuid4().hex[:10]}"


async def _cleanup(db: Database, review_detail_id: int) -> None:
    await db.execute(
        "DELETE FROM review_details WHERE review_detail_id = :review_detail_id",
        {"review_detail_id": review_detail_id},
    )


@pytest.fixture
async def parent(db: Database) -> AsyncIterator[int]:
    """Seed the user/merchant/category/product/review chain and return review_id. `review_details.review_id` has a `REFERENCES reviews(review_id)` FK, so the REST create needs a real parent review."""
    email = f"test_rd_contract_{uuid.uuid4().hex[:10]}@example.com"
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
    product_id = int(product["product_id"])
    review = await db.execute(
        """
        INSERT INTO reviews (user_id, product_id, name, comment, rating)
        VALUES (:uid, :pid, 'reviewer', 'comment', 5)
        RETURNING review_id
        """,
        {"uid": user_id, "pid": product_id},
    )
    assert review is not None
    review_id = int(review["review_id"])
    try:
        yield review_id
    finally:
        await db.execute(
            "DELETE FROM review_details WHERE review_id = :rid", {"rid": review_id}
        )
        await db.execute(
            "DELETE FROM reviews WHERE review_id = :rid", {"rid": review_id}
        )
        await db.execute(
            "DELETE FROM products WHERE product_id = :pid", {"pid": product_id}
        )
        await db.execute(
            "DELETE FROM categories WHERE category_id = :cid", {"cid": category_id}
        )
        await db.execute(
            "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
        )
        await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


async def test_review_detail_rest_contract(
    db: Database, review_detail_grpc_server: str, parent: int, tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(
        review_detail_handler, "_UPLOAD_DIR", str(tmp_path / "review_detail")
    )
    channel = grpc.aio.insecure_channel(review_detail_grpc_server)
    app = _app(review_detail_grpc_server, channel)
    caption = _caption()
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            created = await client.post(
                "/api/review-detail-command/create",
                data={"review_id": str(parent), "type": "photo", "caption": caption},
                files={"url": ("photo.jpg", b"img-bytes", "image/jpeg")},
            )
            assert created.status_code == 201
            review_detail_id = created.json()["data"]["id"]
            assert review_detail_id > 0
            assert created.json()["data"]["id"] == review_detail_id
            assert created.json()["data"]["caption"] == caption
            assert created.json()["data"]["url"].startswith(
                str(tmp_path / "review_detail")
            )

            listed = await client.get(
                "/api/review-detail-query", params={"search": caption}
            )
            assert listed.status_code == 200
            listed_body = listed.json()
            assert listed_body["pagination"]["total_records"] >= 1
            row = listed_body["data"][0]
            assert row["id"] == review_detail_id
            assert row["caption"] == caption
            assert len(row["created_at"]) == 10  # date-only

            by_id = await client.get(f"/api/review-detail-query/{review_detail_id}")
            assert by_id.status_code == 200
            assert by_id.json()["data"]["id"] == review_detail_id

            active = await client.get(
                "/api/review-detail-query/active", params={"search": caption}
            )
            assert active.status_code == 200
            assert (
                active.json()["message"] == "Successfully fetched active review details"
            )

            trashed_list = await client.get(
                "/api/review-detail-query/trashed", params={"search": caption}
            )
            assert trashed_list.status_code == 200
            assert (
                trashed_list.json()["message"]
                == "Successfully fetched trashed review details"
            )

            # Static `/active` must win over `/{review_detail_id}`.
            assert active.json()["status"] == "success"

            # gRPC FindById guards id == 0 -> 400 invalid ID (gateway forwards it).
            bad_id = await client.get("/api/review-detail-query/0")
            assert bad_id.status_code == 400
            assert bad_id.json()["message"] == "invalid ID"

            bad_trash = await client.post("/api/review-detail-command/trashed/0")
            assert bad_trash.status_code == 400
            assert bad_trash.json()["message"] == "Invalid ID"

            missing = await client.post(
                "/api/review-detail-command/trashed/2000000000"
            )
            assert missing.status_code == 404
            assert missing.json()["type"] == "NOT_FOUND"

            trashed = await client.post(
                f"/api/review-detail-command/trashed/{review_detail_id}"
            )
            assert trashed.status_code == 200
            assert trashed.json()["message"] == "Successfully trashed review detail"
            assert trashed.json()["data"]["deleted_at"]

            # FindAll does NOT filter deleted_at, so the trashed row is
            # still present in the list endpoint.
            after_trash = await client.get(
                "/api/review-detail-query", params={"search": caption}
            )
            assert any(
                r["id"] == review_detail_id for r in after_trash.json()["data"]
            )

            in_trash = await client.get(
                "/api/review-detail-query/trashed", params={"search": caption}
            )
            assert any(r["id"] == review_detail_id for r in in_trash.json()["data"])

            # find_active excludes the trashed row.
            active_after = await client.get(
                "/api/review-detail-query/active", params={"search": caption}
            )
            assert all(
                r["id"] != review_detail_id for r in active_after.json()["data"]
            )

            # find_by_id excludes trashed rows -> 404.
            by_id_trashed = await client.get(
                f"/api/review-detail-query/{review_detail_id}"
            )
            assert by_id_trashed.status_code == 404

            restored = await client.post(
                f"/api/review-detail-command/restore/{review_detail_id}"
            )
            assert restored.status_code == 200
            assert restored.json()["data"]["id"] == review_detail_id

            # Static path must win over `/restore/{review_detail_id}`.
            restore_all = await client.post("/api/review-detail-command/restore/all")
            assert restore_all.status_code == 200
            assert restore_all.json()["message"] == "Successfully restored all review details"

            await client.post(f"/api/review-detail-command/trashed/{review_detail_id}")
            deleted = await client.delete(
                f"/api/review-detail-command/permanent/{review_detail_id}"
            )
            assert deleted.status_code == 200
            assert deleted.json()["message"] == "Successfully deleted review detail permanently"

            permanent_all = await client.post(
                "/api/review-detail-command/permanent/all"
            )
            assert permanent_all.status_code == 200
            assert (
                permanent_all.json()["message"]
                == "Successfully deleted all review details permanently"
            )
    finally:
        await channel.close()
        # The review detail may already be hard-deleted; ignore if gone.
        try:
            await _cleanup(db, review_detail_id)
        except Exception:
            pass


async def test_review_detail_string_url_fallback(
    db: Database, review_detail_grpc_server: str, parent: int
) -> None:
    """A text `url` form field is forwarded unchanged (no upload)."""
    channel = grpc.aio.insecure_channel(review_detail_grpc_server)
    app = _app(review_detail_grpc_server, channel)
    caption = _caption()
    transport = httpx.ASGITransport(app=app)
    review_detail_id = None

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            created = await client.post(
                "/api/review-detail-command/create",
                data={
                    "review_id": str(parent),
                    "type": "photo",
                    "caption": caption,
                    "url": "https://cdn.example.com/a.png",
                },
            )
            assert created.status_code == 201
            review_detail_id = created.json()["data"]["id"]
            assert created.json()["data"]["url"] == "https://cdn.example.com/a.png"
    finally:
        await channel.close()
        if review_detail_id is not None:
            try:
                await _cleanup(db, review_detail_id)
            except Exception:
                pass


__all__ = []
