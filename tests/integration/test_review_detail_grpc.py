"""Review detail gRPC integration tests: real grpc.aio server, generated client.

Marked `integration`. Verifies the wire contract (date-only timestamps, the
`deleted_at` wrapper only on the `...DeleteAt` projections, `type` field) and
that the `ErrorResponse` detail survives the hop, so a 400/404 stays a 400/404.

Unlike slider, the gRPC `FindById` handler guards `id == 0` with a bare 400
`invalid ID`. The command handlers (`Update`/`TrashedReviewDetail`/
`RestoreReviewDetail`/`DeleteReviewDetailPermanent`) also guard `id <= 0`. The
`FindAll` projection does NOT filter `deleted_at`, so a trashed row still appears
in `FindAll` (only `FindByActive`/`FindByTrashed`/`FindById` filter it).
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.review import review_query_pb2
from pb.review_detail import (
    review_detail_command_pb2,
    review_detail_command_pb2_grpc,
    review_detail_common_pb2,
    review_detail_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


def _caption() -> str:
    return f"Caption {uuid.uuid4().hex[:10]}"


async def _cleanup(db: Database, review_detail_id: int) -> None:
    await db.execute(
        "DELETE FROM review_details WHERE review_detail_id = :review_detail_id",
        {"review_detail_id": review_detail_id},
    )


@pytest.fixture
async def parent(db: Database) -> AsyncIterator[int]:
    """Seed the user/merchant/category/product/review chain and return review_id.

    `review_details.review_id` now has a `REFERENCES reviews(review_id)` FK, so a
    detail cannot be created without a real parent review.
    """
    email = f"test_rd_grpc_{uuid.uuid4().hex[:10]}@example.com"
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


async def test_review_detail_grpc_lifecycle_and_error_mapping(
    db: Database, review_detail_grpc_server: str, parent: int
) -> None:
    channel = grpc.aio.insecure_channel(review_detail_grpc_server)
    query = review_detail_query_pb2_grpc.ReviewDetailQueryServiceStub(channel)
    command = review_detail_command_pb2_grpc.ReviewDetailCommandServiceStub(channel)
    caption = _caption()

    try:
        created = await command.Create(
            review_detail_command_pb2.CreateReviewDetailRequest(
                review_id=parent, type="photo", url="/img/a.png", caption=caption
            ),
            timeout=5,
        )
        assert created.status == "success"
        assert created.message == "Successfully created review detail"
        assert created.data.caption == caption
        assert created.data.created_at
        assert len(created.data.created_at) == 10  # date-only
        review_detail_id = created.data.id

        found = await query.FindById(
            review_detail_common_pb2.FindByIdReviewDetailRequest(id=review_detail_id),
            timeout=5,
        )
        assert found.message == "Successfully fetched review detail"
        assert found.data.id == review_detail_id

        listed = await query.FindAll(
            review_query_pb2.FindAllReviewRequest(page=1, page_size=10, search=caption),
            timeout=5,
        )
        assert listed.pagination.total_records >= 1

        trashed = await command.TrashedReviewDetail(
            review_detail_common_pb2.FindByIdReviewDetailRequest(id=review_detail_id),
            timeout=5,
        )
        assert trashed.message == "Successfully trashed review detail"
        assert trashed.data.deleted_at.value

        # FindAll does NOT filter deleted_at.
        listed_after = await query.FindAll(
            review_query_pb2.FindAllReviewRequest(page=1, page_size=10, search=caption),
            timeout=5,
        )
        assert any(row.id == review_detail_id for row in listed_after.data)

        trashed_rows = await query.FindByTrashed(
            review_query_pb2.FindAllReviewRequest(page=1, page_size=10, search=caption),
            timeout=5,
        )
        assert any(
            row.id == review_detail_id and row.deleted_at.value
            for row in trashed_rows.data
        )

        restored = await command.RestoreReviewDetail(
            review_detail_common_pb2.FindByIdReviewDetailRequest(id=review_detail_id),
            timeout=5,
        )
        assert restored.message == "Successfully restored review detail"

        # Query FindById guards id == 0 with a bare 400 invalid ID.
        with pytest.raises(grpc.aio.AioRpcError) as invalid_query:
            await query.FindById(
                review_detail_common_pb2.FindByIdReviewDetailRequest(id=0), timeout=5
            )
        assert invalid_query.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        parsed_invalid = parse_grpc_error(invalid_query.value)
        assert parsed_invalid.code == 400
        assert parsed_invalid.message == "invalid ID"

        # Command handlers guard id == 0 with a bare 400 invalid ID.
        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await command.TrashedReviewDetail(
                review_detail_common_pb2.FindByIdReviewDetailRequest(id=0), timeout=5
            )
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        parsed = parse_grpc_error(invalid.value)
        assert parsed.code == 400
        assert parsed.message == "invalid ID"

        # A repository 404 is preserved as NOT_FOUND (ToGrpcError semantics).
        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await command.TrashedReviewDetail(
                review_detail_common_pb2.FindByIdReviewDetailRequest(id=2_000_000_000),
                timeout=5,
            )
        assert missing.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing.value).code == 404

        await command.TrashedReviewDetail(
            review_detail_common_pb2.FindByIdReviewDetailRequest(id=review_detail_id),
            timeout=5,
        )
        deleted = await command.DeleteReviewDetailPermanent(
            review_detail_common_pb2.FindByIdReviewDetailRequest(id=review_detail_id),
            timeout=5,
        )
        assert deleted.message == "Successfully deleted review detail permanently"
    finally:
        await channel.close()
        await _cleanup(db, review_detail_id)


async def test_restore_all_and_delete_all_over_grpc(
    db: Database, review_detail_grpc_server: str, parent: int
) -> None:
    channel = grpc.aio.insecure_channel(review_detail_grpc_server)
    command = review_detail_command_pb2_grpc.ReviewDetailCommandServiceStub(channel)
    query = review_detail_query_pb2_grpc.ReviewDetailQueryServiceStub(channel)
    caption = _caption()
    created = await command.Create(
        review_detail_command_pb2.CreateReviewDetailRequest(
            review_id=parent, type="photo", url="/img/a.png", caption=caption
        ),
        timeout=5,
    )
    review_detail_id = created.data.id
    try:
        await command.TrashedReviewDetail(
            review_detail_common_pb2.FindByIdReviewDetailRequest(id=review_detail_id),
            timeout=5,
        )

        restored_all = await command.RestoreAllReviewDetail(
            empty_pb2.Empty(), timeout=5
        )
        assert restored_all.message == "Successfully restored all review details"

        active = await query.FindByActive(
            review_query_pb2.FindAllReviewRequest(page=1, page_size=10, search=caption),
            timeout=5,
        )
        assert any(row.id == review_detail_id for row in active.data)

        await command.TrashedReviewDetail(
            review_detail_common_pb2.FindByIdReviewDetailRequest(id=review_detail_id),
            timeout=5,
        )
        deleted_all = await command.DeleteAllReviewDetailPermanent(
            empty_pb2.Empty(), timeout=5
        )
        assert deleted_all.message == "Successfully deleted all review details permanently"

        trashed_rows = await query.FindByTrashed(
            review_query_pb2.FindAllReviewRequest(page=1, page_size=10, search=caption),
            timeout=5,
        )
        assert all(row.id != review_detail_id for row in trashed_rows.data)
    finally:
        await channel.close()
        await _cleanup(db, review_detail_id)


__all__ = []
