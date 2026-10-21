"""review repository integration tests. Marked `integration` (excluded from `make test`)."""

from __future__ import annotations

import uuid
from typing import Any

import grpc
import pytest

from service.review.repository import GuardOptions, new_repositories
from shared.domain.requests.review import (
    CreateReviewRecord,
    FindAllReviews,
    FindAllReviewsByMerchant,
    FindAllReviewsByProduct,
    UpdateReviewRequest,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


@pytest.fixture
async def repos(db):
    """review repositories with unused user/product channels."""
    user_channel = grpc.aio.insecure_channel("127.0.0.1:1")
    product_channel = grpc.aio.insecure_channel("127.0.0.1:1")
    try:
        yield new_repositories(
            db,
            user_channel=user_channel,
            product_channel=product_channel,
            guards=GuardOptions(),
        )
    finally:
        await user_channel.close()
        await product_channel.close()


async def _seed(db) -> tuple[int, int, int, int]:
    """Seed user + merchant + category + product; return their ids."""
    email = f"test_review_{uuid.uuid4().hex[:10]}@example.com"
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


async def _cleanup(db, user_id: int, merchant_id: int, category_id: int) -> None:
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


def _record(user_id: int, product_id: int, **overrides: Any) -> CreateReviewRecord:
    base = CreateReviewRecord(
        user_id=user_id,
        product_id=product_id,
        name="",
        comment=f"Review {uuid.uuid4().hex[:8]}",
        rating=5,
    )
    return CreateReviewRecord(
        user_id=base.user_id,
        product_id=base.product_id,
        name=base.name,
        comment=overrides.get("comment", base.comment),
        rating=overrides.get("rating", base.rating),
    )


async def test_create_find_all_and_find_by_id(db, repos) -> None:
    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        comment = f"Bagus {uuid.uuid4().hex[:8]}"
        created = await repos.review_command.create(
            _record(user_id, product_id, comment=comment, rating=4)
        )
        assert created.review_id > 0
        assert created.user_id == user_id
        assert created.product_id == product_id
        assert created.name == ""  # request carries no name
        assert created.comment == comment
        assert created.rating == 4

        rows = await repos.review_query.find_all(
            FindAllReviews(search=str(created.review_id), page=1, page_size=10)
        )
        assert any(row.review_id == created.review_id for row in rows)
        assert rows[0].total_count >= 1

        by_id = await repos.review_query.find_by_id(created.review_id)
        assert by_id.review_id == created.review_id
        assert by_id.comment == comment
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_find_all_search_matches_id_and_name(db, repos) -> None:
    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        name = f"Reviewer {uuid.uuid4().hex[:8]}"
        created = await repos.review_command.create(
            _record(user_id, product_id, comment="hello")
        )
        await repos.review_command.update(
            UpdateReviewRequest(
                review_id=created.review_id, name=name, rating=5, comment="hello"
            )
        )

        by_name = await repos.review_query.find_all(
            FindAllReviews(search=name, page=1, page_size=10)
        )
        assert any(row.review_id == created.review_id for row in by_name)

        by_id = await repos.review_query.find_all(
            FindAllReviews(search=str(created.review_id), page=1, page_size=10)
        )
        assert any(row.review_id == created.review_id for row in by_id)
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_find_by_product_aggregates_details_and_rating_filter(db, repos) -> None:
    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        created = await repos.review_command.create(
            _record(user_id, product_id, comment="with detail", rating=3)
        )
        await db.execute(
            """
            INSERT INTO review_details (review_id, type, url, caption)
            VALUES (:rid, 'photo', '/img/a.png', 'cap')
            """,
            {"rid": created.review_id},
        )

        rows = await repos.review_query.find_by_product(
            FindAllReviewsByProduct(
                product_id=product_id, rating=0, search="", page=1, page_size=10
            )
        )
        assert len(rows) >= 1
        row = next(r for r in rows if r.review_id == created.review_id)
        assert row.review_details is not None
        assert row.review_details[0]["type"] == "photo"
        assert row.review_details[0]["caption"] == "cap"

        # rating = 0 -> all ratings (normalised from broken `= 0`).
        all_rows = await repos.review_query.find_by_product(
            FindAllReviewsByProduct(
                product_id=product_id, rating=0, search="", page=1, page_size=10
            )
        )
        assert any(r.review_id == created.review_id for r in all_rows)

        # A non-matching rating filters it out.
        none_rows = await repos.review_query.find_by_product(
            FindAllReviewsByProduct(
                product_id=product_id, rating=5, search="", page=1, page_size=10
            )
        )
        assert all(r.review_id != created.review_id for r in none_rows)
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_find_by_merchant(db, repos) -> None:
    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        created = await repos.review_command.create(
            _record(user_id, product_id, comment="merchant review")
        )
        rows = await repos.review_query.find_by_merchant(
            FindAllReviewsByMerchant(
                merchant_id=merchant_id, rating=0, search="", page=1, page_size=10
            )
        )
        assert any(r.review_id == created.review_id for r in rows)
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_update_trash_restore_and_active_trashed(db, repos) -> None:
    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        created = await repos.review_command.create(
            _record(user_id, product_id, comment="before")
        )
        updated = await repos.review_command.update(
            UpdateReviewRequest(
                review_id=created.review_id, name="N", rating=2, comment="after"
            )
        )
        assert updated.comment == "after"
        assert updated.rating == 2

        trashed = await repos.review_command.trash(created.review_id)
        assert trashed.deleted_at is not None

        active = await repos.review_query.find_active(
            FindAllReviews(search="", page=1, page_size=100)
        )
        assert all(r.review_id != created.review_id for r in active)

        trashed_rows = await repos.review_query.find_trashed(
            FindAllReviews(search="", page=1, page_size=100)
        )
        assert any(r.review_id == created.review_id for r in trashed_rows)

        restored = await repos.review_command.restore(created.review_id)
        assert restored.deleted_at is None
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_delete_permanent_requires_trashed(db, repos) -> None:
    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        created = await repos.review_command.create(
            _record(user_id, product_id, comment="delete me")
        )
        # delete_permanent only removes trashed rows (`:exec` -> always True).
        assert await repos.review_command.delete_permanent(created.review_id) is True
        still_active = await repos.review_query.find_by_id(created.review_id)
        assert still_active.review_id == created.review_id

        await repos.review_command.trash(created.review_id)
        assert await repos.review_command.delete_permanent(created.review_id) is True
        with pytest.raises(AppError) as missing:
            await repos.review_query.find_by_id(created.review_id)
        assert missing.value.code == 404
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_pagination_reports_total_count(db, repos) -> None:
    user_id, product_id, merchant_id, category_id = await _seed(db)
    try:
        prefix = f"Bulk {uuid.uuid4().hex[:6]}"
        for index in range(3):
            created = await repos.review_command.create(
                _record(user_id, product_id, comment=f"{prefix}-{index}")
            )
            # `find_all` matches on `name`, so give each review a searchable name.
            await repos.review_command.update(
                UpdateReviewRequest(
                    review_id=created.review_id,
                    name=f"{prefix}-{index}",
                    rating=5,
                    comment=f"{prefix}-{index}",
                )
            )
        rows = await repos.review_query.find_all(
            FindAllReviews(search=prefix, page=1, page_size=2)
        )
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        await _cleanup(db, user_id, merchant_id, category_id)


async def test_missing_review_maps_to_not_found(db, repos) -> None:
    with pytest.raises(AppError) as excinfo:
        await repos.review_query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "review not found"


__all__ = []
