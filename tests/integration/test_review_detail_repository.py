"""Review detail repository integration tests against a real PostgreSQL. Marked `integration` (excluded from `make test`). `review_details.review_id` has a `REFERENCES reviews(review_id) ON DELETE CASCADE` FK (added when the `review` stage landed), so the `parent` fixture seeds the full user/merchant/category/ product/review chain each test needs and tears it down afterwards. A unique `caption` token is used as the search key (the SQL matches `COALESCE(caption, '') ILIKE`)."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

import pytest

from service.review_detail.repository import new_repositories
from shared.domain.requests.review_detail import (
    CreateReviewDetailRequest,
    UpdateReviewDetailRequest,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


def _caption() -> str:
    return f"Caption {uuid.uuid4().hex[:10]}"


def _create(review_id: int, caption: str) -> CreateReviewDetailRequest:
    return CreateReviewDetailRequest(
        review_id=review_id,
        type="photo",
        url=f"/img/{uuid.uuid4().hex[:6]}.png",
        caption=caption,
    )


async def _cleanup(db, review_detail_id: int) -> None:
    await db.execute(
        "DELETE FROM review_details WHERE review_detail_id = :review_detail_id",
        {"review_detail_id": review_detail_id},
    )


@pytest.fixture
async def parent(db) -> AsyncIterator[int]:
    """Seed the user/merchant/category/product/review chain and return review_id."""
    email = f"test_rd_{uuid.uuid4().hex[:10]}@example.com"
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


async def test_create_and_find(db, parent: int) -> None:
    repos = new_repositories(db)
    caption = _caption()
    try:
        created = await repos.command.create(_create(parent, caption))
        assert created.review_detail_id > 0
        assert created.caption == caption
        assert created.type == "photo"

        by_id = await repos.query.find_by_id(created.review_detail_id)
        assert by_id.review_detail_id == created.review_detail_id

        listed = await repos.query.find_all(caption, 1, 10)
        assert any(
            row.review_detail_id == created.review_detail_id for row in listed
        )
    finally:
        await _cleanup(db, created.review_detail_id)


async def test_soft_delete_lifecycle(db, parent: int) -> None:
    repos = new_repositories(db)
    caption = _caption()
    created = await repos.command.create(_create(parent, caption))
    try:
        trashed = await repos.command.trash(created.review_detail_id)
        assert trashed.deleted_at is not None

        # FindAll does NOT filter deleted_at, so the row is still listed.
        listed = await repos.query.find_all(caption, 1, 10)
        assert any(
            row.review_detail_id == created.review_detail_id for row in listed
        )

        active = await repos.query.find_active(caption, 1, 10)
        assert all(
            row.review_detail_id != created.review_detail_id for row in active
        )

        trashed_rows = await repos.query.find_trashed(caption, 1, 10)
        assert any(
            row.review_detail_id == created.review_detail_id for row in trashed_rows
        )

        # FindById excludes trashed rows.
        with pytest.raises(AppError) as missing:
            await repos.query.find_by_id(created.review_detail_id)
        assert missing.value.code == 404

        restored = await repos.command.restore(created.review_detail_id)
        assert restored.deleted_at is None

        active_after = await repos.query.find_active(caption, 1, 10)
        assert any(
            row.review_detail_id == created.review_detail_id for row in active_after
        )
    finally:
        await _cleanup(db, created.review_detail_id)


async def test_update_then_delete_permanent(db, parent: int) -> None:
    repos = new_repositories(db)
    caption = _caption()
    created = await repos.command.create(_create(parent, caption))
    try:
        updated = await repos.command.update(
            UpdateReviewDetailRequest(
                review_detail_id=created.review_detail_id,
                type="video",
                url="/img/updated.png",
                caption=f"{caption}-v2",
            )
        )
        assert updated.type == "video"
        assert updated.caption == f"{caption}-v2"

        await repos.command.trash(created.review_detail_id)
        await repos.command.delete_permanent(created.review_detail_id)

        trashed_rows = await repos.query.find_trashed(caption, 1, 10)
        assert all(
            row.review_detail_id != created.review_detail_id for row in trashed_rows
        )
    finally:
        await _cleanup(db, created.review_detail_id)


async def test_pagination_reports_total_count(db, parent: int) -> None:
    repos = new_repositories(db)
    prefix = f"Caption {uuid.uuid4().hex[:10]}"
    ids: list[int] = []
    try:
        for i in range(3):
            row = await repos.command.create(_create(parent, f"{prefix}-{i}"))
            ids.append(row.review_detail_id)
        rows = await repos.query.find_all(prefix, 1, 2)
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        for rid in ids:
            await _cleanup(db, rid)


async def test_delete_permanent_ignores_missing_row(db) -> None:
    """DeleteReviewDetailPermanent ignores RowsAffected (no 404)."""
    repos = new_repositories(db)
    # Should not raise.
    assert await repos.command.delete_permanent(2_000_000_000) is True


async def test_restore_all_restores_trashed(db, parent: int) -> None:
    repos = new_repositories(db)
    caption = _caption()
    created = await repos.command.create(_create(parent, caption))
    try:
        await repos.command.trash(created.review_detail_id)

        await repos.command.restore_all()

        active = await repos.query.find_active(caption, 1, 10)
        assert any(
            row.review_detail_id == created.review_detail_id for row in active
        )
    finally:
        await _cleanup(db, created.review_detail_id)


async def test_delete_all_permanent_clears_trashed(db, parent: int) -> None:
    repos = new_repositories(db)
    caption = _caption()
    created = await repos.command.create(_create(parent, caption))
    try:
        await repos.command.trash(created.review_detail_id)

        await repos.command.delete_all_permanent()

        rows = await repos.query.find_trashed(caption, 1, 10)
        assert all(
            row.review_detail_id != created.review_detail_id for row in rows
        )
    finally:
        await _cleanup(db, created.review_detail_id)


async def test_missing_review_detail_maps_to_not_found(db) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.command.trash(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "review detail not found"


async def test_update_missing_review_detail_maps_to_not_found(db) -> None:
    repos = new_repositories(db)
    with pytest.raises(AppError) as excinfo:
        await repos.command.update(
            UpdateReviewDetailRequest(
                review_detail_id=2_000_000_000, type="photo", url="/a.png", caption="x"
            )
        )
    assert excinfo.value.code == 404


__all__ = []
