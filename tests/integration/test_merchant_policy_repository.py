"""merchant_policy repository integration tests.

Marked `integration` (excluded from `make test`).
`merchant_policies.merchant_id` has a `REFERENCES merchants(merchant_id) ON
DELETE CASCADE` FK, so each test seeds its own user + merchant and removes them
afterwards. A unique merchant name is used as the search key
(`find_all`/`find_active`/`find_trashed` search `m.name`).

:
- `find_all` filters `mp.deleted_at IS NULL` but NOT `m.deleted_at`, while
 `find_active` additionally requires `m.deleted_at IS NULL`;
- `find_trashed` filters `mp.deleted_at IS NOT NULL`;
- `find_by_id` adds `AND deleted_at IS NULL` and maps a missing row to 404;
- `delete_permanent` only affects trashed rows (`deleted_at IS NOT NULL`);
- the window `COUNT(*)` supplies `total_count`."""

from __future__ import annotations

import uuid

import grpc
import pytest

from service.merchant_policy.repository import GuardOptions, new_repositories
from shared.domain.requests.merchant_policy import (
    CreateMerchantPolicyRequest,
    UpdateMerchantPolicyRequest,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


@pytest.fixture
async def repos(db):
    """merchant_policy repositories with an unused merchant channel."""
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    try:
        yield new_repositories(db, merchant_channel=channel, guards=GuardOptions())
    finally:
        await channel.close()


async def _seed_merchant(db) -> tuple[int, int, str]:
    email = f"test_merchant_policy_{uuid.uuid4().hex[:10]}@example.com"
    name = f"Merchant {uuid.uuid4().hex[:10]}"
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
        {"user_id": user_id, "name": name},
    )
    assert merchant is not None
    return user_id, int(merchant["merchant_id"]), name


async def _cleanup(db, user_id: int, merchant_id: int) -> None:
    await db.execute(
        "DELETE FROM merchant_policies WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


def _create(merchant_id: int, **overrides) -> CreateMerchantPolicyRequest:
    values = {
        "merchant_id": merchant_id,
        "policy_type": "Shipping",
        "title": "Free Shipping on Orders Above $50",
        "description": "desc",
    }
    values.update(overrides)
    return CreateMerchantPolicyRequest(**values)


async def test_create_and_find(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_policy_command.create(_create(merchant_id))
        assert created.merchant_policy_id > 0
        assert created.policy_type == "Shipping"
        assert created.title == "Free Shipping on Orders Above $50"

        by_id = await repos.merchant_policy_query.find_by_id(
            created.merchant_policy_id
        )
        assert by_id.merchant_policy_id == created.merchant_policy_id
        assert by_id.description == "desc"

        listed = await repos.merchant_policy_query.find_all(name, 1, 10)
        assert any(
            row.merchant_policy_id == created.merchant_policy_id for row in listed
        )
        assert listed[0].total_count >= 1
        assert listed[0].merchant_name == name
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_update_changes_fields(db, repos) -> None:
    user_id, merchant_id, _ = await _seed_merchant(db)
    try:
        created = await repos.merchant_policy_command.create(_create(merchant_id))
        updated = await repos.merchant_policy_command.update(
            UpdateMerchantPolicyRequest(
                merchant_policy_id=created.merchant_policy_id,
                policy_type="Refund",
                title="30-Day Refund Policy",
                description="updated",
            )
        )
        assert updated.policy_type == "Refund"
        assert updated.title == "30-Day Refund Policy"
        assert updated.description == "updated"
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_soft_delete_lifecycle(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_policy_command.create(_create(merchant_id))
        policy_id = created.merchant_policy_id

        trashed = await repos.merchant_policy_command.trash(policy_id)
        assert trashed.deleted_at is not None

        listed = await repos.merchant_policy_query.find_all(name, 1, 10)
        assert all(row.merchant_policy_id != policy_id for row in listed)
        active = await repos.merchant_policy_query.find_active(name, 1, 10)
        assert all(row.merchant_policy_id != policy_id for row in active)
        trashed_rows = await repos.merchant_policy_query.find_trashed(name, 1, 10)
        assert any(row.merchant_policy_id == policy_id for row in trashed_rows)

        with pytest.raises(AppError) as missing:
            await repos.merchant_policy_query.find_by_id(policy_id)
        assert missing.value.code == 404

        restored = await repos.merchant_policy_command.restore(policy_id)
        assert restored.deleted_at is None
        active_after = await repos.merchant_policy_query.find_active(name, 1, 10)
        assert any(row.merchant_policy_id == policy_id for row in active_after)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_find_all_ignores_merchant_deleted_but_find_active_does_not(
    db, repos
) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_policy_command.create(_create(merchant_id))
        policy_id = created.merchant_policy_id

        await db.execute(
            "UPDATE merchants SET deleted_at = CURRENT_TIMESTAMP WHERE merchant_id = :mid",
            {"mid": merchant_id},
        )

        listed = await repos.merchant_policy_query.find_all(name, 1, 10)
        assert any(row.merchant_policy_id == policy_id for row in listed)

        active = await repos.merchant_policy_query.find_active(name, 1, 10)
        assert all(row.merchant_policy_id != policy_id for row in active)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_delete_permanent_requires_trashed(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_policy_command.create(_create(merchant_id))
        policy_id = created.merchant_policy_id

        # A live row is not deleted (SQL guards deleted_at IS NOT NULL).
        await repos.merchant_policy_command.delete_permanent(policy_id)
        still_there = await repos.merchant_policy_query.find_by_id(policy_id)
        assert still_there.merchant_policy_id == policy_id

        await repos.merchant_policy_command.trash(policy_id)
        await repos.merchant_policy_command.delete_permanent(policy_id)
        trashed_rows = await repos.merchant_policy_query.find_trashed(name, 1, 10)
        assert all(row.merchant_policy_id != policy_id for row in trashed_rows)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_missing_maps_to_not_found(db, repos) -> None:
    with pytest.raises(AppError) as excinfo:
        await repos.merchant_policy_query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "merchant policy not found"

    with pytest.raises(AppError) as trash_missing:
        await repos.merchant_policy_command.trash(2_000_000_000)
    assert trash_missing.value.code == 404


async def test_pagination_reports_total_count(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        for _ in range(3):
            await repos.merchant_policy_command.create(_create(merchant_id))
        rows = await repos.merchant_policy_query.find_all(name, 1, 2)
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_restore_all_and_delete_all(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_policy_command.create(_create(merchant_id))
        policy_id = created.merchant_policy_id
        await repos.merchant_policy_command.trash(policy_id)

        await repos.merchant_policy_command.restore_all()
        active = await repos.merchant_policy_query.find_active(name, 1, 10)
        assert any(row.merchant_policy_id == policy_id for row in active)

        await repos.merchant_policy_command.trash(policy_id)
        await repos.merchant_policy_command.delete_all()
        trashed_rows = await repos.merchant_policy_query.find_trashed(name, 1, 10)
        assert all(row.merchant_policy_id != policy_id for row in trashed_rows)
    finally:
        await _cleanup(db, user_id, merchant_id)


__all__ = []
