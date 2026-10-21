"""review gRPC integration tests. Marked `integration`. Runs the two real review servicers behind an ephemeral port; the `review_grpc_server` fixture points the review user/product adapters at the real user and product servers (both spun up by their own fixtures). Tests seed the real user + merchant + category + product rows the review FKs and adapters need. Verifies the wire contract (date-only `%Y-%m-%d` for plain rows, `.mmm` for the detail rows, the always-present `deleted_at` wrapper) and the error mapping: - an invalid update body -> 400 `validation failed: invalid update review request`; - `id == 0` on a single-row command -> 400 `invalid ID`; - a missing product -> 404 `product not found` (adapter); - a missing author -> 404 (user adapter)."""

from __future__ import annotations

import uuid

import grpc
import pytest

from pb.review import (
    review_command_pb2,
    review_command_pb2_grpc,
    review_common_pb2,
    review_query_pb2,
    review_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


async def _seed(db: Database) -> tuple[int, int, int, int]:
    email = f"test_review_grpc_{uuid.uuid4().hex[:10]}@example.com"
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


async def test_review_grpc_lifecycle(db: Database, review_grpc_server: str) -> None:
    channel = grpc.aio.insecure_channel(review_grpc_server)
    query = review_query_pb2_grpc.ReviewQueryServiceStub(channel)
    command = review_command_pb2_grpc.ReviewCommandServiceStub(channel)

    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        created = await command.Create(
            review_command_pb2.CreateReviewRequest(
                user_id=user_id, product_id=product_id, comment="Produk bagus!", rating=5
            ),
            timeout=5,
        )
        assert created.message == "Successfully created review"
        assert created.data.user_id == user_id
        assert created.data.product_id == product_id
        assert created.data.comment == "Produk bagus!"
        assert created.data.rating == 5
        assert len(created.data.created_at) == 10  # date-only
        review_id = created.data.id

        # A second review stays active so `FindByActive` is guaranteed non-empty
        # after the first is trashed.
        other = await command.Create(
            review_command_pb2.CreateReviewRequest(
                user_id=user_id, product_id=product_id, comment="Lain", rating=3
            ),
            timeout=5,
        )
        assert other.data.id != review_id

        listed = await query.FindAll(
            review_query_pb2.FindAllReviewRequest(page=1, page_size=10), timeout=5
        )
        assert listed.message == "Successfully fetched reviews"
        assert listed.pagination.total_records >= 1
        assert any(r.id == review_id for r in listed.data)

        by_product = await query.FindByProduct(
            review_query_pb2.FindAllReviewProductRequest(
                product_id=product_id, page=1, page_size=10
            ),
            timeout=5,
        )
        assert by_product.message == "Successfully fetched product reviews"
        # Detail rows use the .mmm timestamp layout.
        assert len(by_product.data[0].created_at) == 23

        by_merchant = await query.FindByMerchant(
            review_query_pb2.FindAllReviewMerchantRequest(
                merchant_id=merchant_id, page=1, page_size=10
            ),
            timeout=5,
        )
        assert any(r.id == review_id for r in by_merchant.data)

        updated = await command.Update(
            review_command_pb2.UpdateReviewRequest(
                review_id=review_id, comment="updated", rating=4
            ),
            timeout=5,
        )
        assert updated.message == "Successfully updated review"
        assert updated.data.comment == "updated"

        trashed = await command.TrashedReview(
            review_common_pb2.FindByIdReviewRequest(id=review_id), timeout=5
        )
        assert trashed.message == "Successfully trashed review"
        assert trashed.data.deleted_at.value  # date-only

        active = await query.FindByActive(
            review_query_pb2.FindAllReviewRequest(page=1, page_size=100), timeout=5
        )
        assert all(r.id != review_id for r in active.data)
        # Active rows still carry the (empty) deleted_at wrapper.
        assert active.data[0].HasField("deleted_at")

        trashed_rows = await query.FindByTrashed(
            review_query_pb2.FindAllReviewRequest(page=1, page_size=100), timeout=5
        )
        assert any(r.id == review_id for r in trashed_rows.data)

        restored = await command.RestoreReview(
            review_common_pb2.FindByIdReviewRequest(id=review_id), timeout=5
        )
        assert restored.message == "Successfully restored review"

        await command.TrashedReview(
            review_common_pb2.FindByIdReviewRequest(id=review_id), timeout=5
        )
        deleted = await command.DeleteReviewPermanent(
            review_common_pb2.FindByIdReviewRequest(id=review_id), timeout=5
        )
        assert deleted.message == "Successfully deleted review permanently"
    finally:
        await channel.close()
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_review_grpc_error_mapping(
    db: Database, review_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(review_grpc_server)
    command = review_command_pb2_grpc.ReviewCommandServiceStub(channel)

    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        # Invalid update body (rating/comment required).
        with pytest.raises(grpc.aio.AioRpcError) as bad_body:
            await command.Update(
                review_command_pb2.UpdateReviewRequest(
                    review_id=1, comment="", rating=0
                ),
                timeout=5,
            )
        assert bad_body.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert parse_grpc_error(bad_body.value).message == (
            "validation failed: invalid update review request"
        )

        # Single-row command with id == 0.
        with pytest.raises(grpc.aio.AioRpcError) as invalid_id:
            await command.TrashedReview(
                review_common_pb2.FindByIdReviewRequest(id=0), timeout=5
            )
        assert invalid_id.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        assert parse_grpc_error(invalid_id.value).message == "invalid ID"

        # A missing product is remapped to the product-not-found sentinel (404).
        with pytest.raises(grpc.aio.AioRpcError) as missing_product:
            await command.Create(
                review_command_pb2.CreateReviewRequest(
                    user_id=user_id, product_id=2_000_000_000, comment="c", rating=5
                ),
                timeout=5,
            )
        assert missing_product.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing_product.value).code == 404

        # A missing author fails the user adapter (404).
        with pytest.raises(grpc.aio.AioRpcError) as missing_user:
            await command.Create(
                review_command_pb2.CreateReviewRequest(
                    user_id=2_000_000_000, product_id=product_id, comment="c", rating=5
                ),
                timeout=5,
            )
        assert missing_user.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing_user.value).code == 404
    finally:
        await channel.close()
        await _cleanup(db, user_id, merchant_id, category_id)


__all__ = []
