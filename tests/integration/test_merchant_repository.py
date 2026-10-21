"""Merchant repository integration tests against a real PostgreSQL. Marked `integration` (excluded from `make test`). `merchants.user_id` has a `REFERENCES users(user_id)` FK, so each test seeds its own user and removes both the merchant and the user afterwards. A unique `name` is used as the search key."""

from __future__ import annotations

import uuid

import grpc
import pytest

from service.merchant.repository import GuardOptions, new_repositories
from shared.domain.requests.merchant import (
    CreateMerchantRequest,
    UpdateMerchantRequest,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


@pytest.fixture
async def repos(db):
    """Merchant repositories with an unused user channel (repository-level test)."""
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    try:
        yield new_repositories(db, user_channel=channel, guards=GuardOptions())
    finally:
        await channel.close()


def _name() -> str:
    return f"Merchant {uuid.uuid4().hex[:10]}"


async def _seed_user(db) -> int:
    email = f"test_merchant_{uuid.uuid4().hex[:10]}@example.com"
    row = await db.execute(
        """
        INSERT INTO users (firstname, lastname, email, password, verification_code)
        VALUES ('T', 'U', :email, 'x', 'v')
        RETURNING user_id
        """,
        {"email": email},
    )
    assert row is not None
    return int(row["user_id"])


async def _cleanup_many(db, merchant_ids: list[int], user_id: int) -> None:
    for merchant_id in merchant_ids:
        await db.execute(
            "DELETE FROM merchant_documents WHERE merchant_id = :merchant_id",
            {"merchant_id": merchant_id},
        )
        await db.execute(
            "DELETE FROM merchants WHERE merchant_id = :merchant_id",
            {"merchant_id": merchant_id},
        )
    await db.execute("DELETE FROM users WHERE user_id = :user_id", {"user_id": user_id})


async def _cleanup(db, merchant_id: int | None, user_id: int) -> None:
    await _cleanup_many(db, [] if merchant_id is None else [merchant_id], user_id)


def _create(user_id: int, name: str) -> CreateMerchantRequest:
    return CreateMerchantRequest(
        user_id=user_id,
        name=name,
        description="desc",
        address="addr",
        contact_email="owner@example.com",
        contact_phone="0812",
        status="inactive",  # ignored on create (hardcodes active)
    )


async def test_create_and_find(db, repos) -> None:
    user_id = await _seed_user(db)
    name = _name()
    merchant_id = None
    try:
        created = await repos.merchant_command.create(_create(user_id, name))
        merchant_id = created.merchant_id
        assert created.merchant_id > 0
        assert created.name == name
        assert created.status == "active"  # create ignores the body status

        by_id = await repos.merchant_query.find_by_id(merchant_id)
        assert by_id.merchant_id == merchant_id

        listed = await repos.merchant_query.find_all(name, 1, 10)
        assert any(row.merchant_id == merchant_id for row in listed)
        assert listed[0].total_count >= 1
    finally:
        await _cleanup(db, merchant_id, user_id)


async def test_update_changes_fields(db, repos) -> None:
    user_id = await _seed_user(db)
    name = _name()
    merchant_id = None
    try:
        created = await repos.merchant_command.create(_create(user_id, name))
        merchant_id = created.merchant_id

        updated = await repos.merchant_command.update(
            UpdateMerchantRequest(
                merchant_id=merchant_id,
                user_id=user_id,
                name=f"{name} v2",
                description="new",
                address="new addr",
                contact_email="new@example.com",
                contact_phone="0899",
                status="inactive",
            )
        )
        assert updated.name == f"{name} v2"
        assert updated.status == "inactive"
    finally:
        await _cleanup(db, merchant_id, user_id)


async def test_soft_delete_lifecycle(db, repos) -> None:
    user_id = await _seed_user(db)
    name = _name()
    merchant_id = None
    try:
        created = await repos.merchant_command.create(_create(user_id, name))
        merchant_id = created.merchant_id

        trashed = await repos.merchant_command.trash(merchant_id)
        assert trashed.deleted_at is not None

        # FindAll/FindActive exclude trashed rows; FindTrashed includes them.
        listed = await repos.merchant_query.find_all(name, 1, 10)
        assert all(row.merchant_id != merchant_id for row in listed)
        active = await repos.merchant_query.find_active(name, 1, 10)
        assert all(row.merchant_id != merchant_id for row in active)
        trashed_rows = await repos.merchant_query.find_trashed(name, 1, 10)
        assert any(row.merchant_id == merchant_id for row in trashed_rows)

        with pytest.raises(AppError) as missing:
            await repos.merchant_query.find_by_id(merchant_id)
        assert missing.value.code == 404

        restored = await repos.merchant_command.restore(merchant_id)
        assert restored.deleted_at is None
        active_after = await repos.merchant_query.find_active(name, 1, 10)
        assert any(row.merchant_id == merchant_id for row in active_after)
    finally:
        await _cleanup(db, merchant_id, user_id)


async def test_delete_permanent_requires_trashed(db, repos) -> None:
    user_id = await _seed_user(db)
    name = _name()
    merchant_id = None
    try:
        created = await repos.merchant_command.create(_create(user_id, name))
        merchant_id = created.merchant_id

        # A live row is not deleted (SQL guards deleted_at IS NOT NULL).
        await repos.merchant_command.delete_permanent(merchant_id)
        still_there = await repos.merchant_query.find_by_id(merchant_id)
        assert still_there.merchant_id == merchant_id

        await repos.merchant_command.trash(merchant_id)
        await repos.merchant_command.delete_permanent(merchant_id)
        trashed_rows = await repos.merchant_query.find_trashed(name, 1, 10)
        assert all(row.merchant_id != merchant_id for row in trashed_rows)
    finally:
        await _cleanup(db, merchant_id, user_id)


async def test_update_missing_maps_to_not_found(db, repos) -> None:
    with pytest.raises(AppError) as excinfo:
        await repos.merchant_command.update(
            UpdateMerchantRequest(
                merchant_id=2_000_000_000,
                user_id=1,
                name="x",
                description="d",
                address="a",
                contact_email="e@f.com",
                contact_phone="0812",
                status="active",
            )
        )
    assert excinfo.value.code == 404


async def test_missing_merchant_maps_to_not_found(db, repos) -> None:
    with pytest.raises(AppError) as excinfo:
        await repos.merchant_query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "merchant not found"

    with pytest.raises(AppError) as trash_missing:
        await repos.merchant_command.trash(2_000_000_000)
    assert trash_missing.value.code == 404


async def test_pagination_reports_total_count(db, repos) -> None:
    user_id = await _seed_user(db)
    prefix = _name()
    ids: list[int] = []
    try:
        for i in range(3):
            row = await repos.merchant_command.create(_create(user_id, f"{prefix}-{i}"))
            ids.append(row.merchant_id)
        rows = await repos.merchant_query.find_all(prefix, 1, 2)
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        await _cleanup_many(db, ids, user_id)


async def test_restore_all_and_delete_all(db, repos) -> None:
    user_id = await _seed_user(db)
    name = _name()
    merchant_id = None
    try:
        created = await repos.merchant_command.create(_create(user_id, name))
        merchant_id = created.merchant_id
        await repos.merchant_command.trash(merchant_id)

        await repos.merchant_command.restore_all()
        active = await repos.merchant_query.find_active(name, 1, 10)
        assert any(row.merchant_id == merchant_id for row in active)

        await repos.merchant_command.trash(merchant_id)
        await repos.merchant_command.delete_all()
        trashed_rows = await repos.merchant_query.find_trashed(name, 1, 10)
        assert all(row.merchant_id != merchant_id for row in trashed_rows)
        merchant_id = None  # already hard-deleted
    finally:
        await _cleanup(db, merchant_id, user_id)


__all__ = []
