"""merchant_business repository integration tests. Marked `integration` (excluded from `make test`). `merchant_business_information.merchant_id` has a `REFERENCES merchants(merchant_id) ON DELETE CASCADE` FK, so each test seeds its own user + merchant and removes them afterwards. A unique merchant name is used as the search key (`find_all`/`find_active`/`find_trashed` search `m.name`).: - `find_all` filters `mbi.deleted_at IS NULL` but NOT `m.deleted_at`, while `find_active` additionally requires `m.deleted_at IS NULL`; - `find_trashed` filters `mbi.deleted_at IS NOT NULL`; - `find_by_id` adds `AND deleted_at IS NULL` and maps a missing row to 404; - `delete_permanent` only affects trashed rows (`deleted_at IS NOT NULL`); - an empty `website_url` is stored as NULL (`stringPtr`)."""

from __future__ import annotations

import uuid

import grpc
import pytest

from service.merchant_business.repository import GuardOptions, new_repositories
from shared.domain.requests.merchant_business import (
    CreateMerchantBusinessInformationRequest,
    UpdateMerchantBusinessInformationRequest,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


@pytest.fixture
async def repos(db):
    """merchant_business repositories with an unused merchant channel."""
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    try:
        yield new_repositories(db, merchant_channel=channel, guards=GuardOptions())
    finally:
        await channel.close()


async def _seed_merchant(db) -> tuple[int, int, str]:
    email = f"test_merchant_business_{uuid.uuid4().hex[:10]}@example.com"
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
        "DELETE FROM merchant_business_information WHERE merchant_id = :mid",
        {"mid": merchant_id},
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


def _create(
    merchant_id: int, **overrides
) -> CreateMerchantBusinessInformationRequest:
    values = {
        "merchant_id": merchant_id,
        "business_type": "Toko Elektronik",
        "tax_id": "01.234.567.8-999.000",
        "established_year": 2010,
        "number_of_employees": 15,
        "website_url": "https://technostore.com",
    }
    values.update(overrides)
    return CreateMerchantBusinessInformationRequest(**values)


async def test_create_and_find(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_business_command.create(_create(merchant_id))
        assert created.merchant_business_info_id > 0
        assert created.business_type == "Toko Elektronik"
        assert created.established_year == 2010
        assert created.number_of_employees == 15

        by_id = await repos.merchant_business_query.find_by_id(
            created.merchant_business_info_id
        )
        assert by_id.merchant_business_info_id == created.merchant_business_info_id
        assert by_id.website_url == "https://technostore.com"

        listed = await repos.merchant_business_query.find_all(name, 1, 10)
        assert any(
            row.merchant_business_info_id == created.merchant_business_info_id
            for row in listed
        )
        assert listed[0].total_count >= 1
        assert listed[0].merchant_name == name
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_update_changes_fields(db, repos) -> None:
    user_id, merchant_id, _ = await _seed_merchant(db)
    try:
        created = await repos.merchant_business_command.create(_create(merchant_id))
        updated = await repos.merchant_business_command.update(
            UpdateMerchantBusinessInformationRequest(
                merchant_business_info_id=created.merchant_business_info_id,
                business_type="Retail Gadget",
                tax_id="04.567.890.1-666.000",
                established_year=2018,
                number_of_employees=8,
                website_url="https://gadgethub.com",
            )
        )
        assert updated.business_type == "Retail Gadget"
        assert updated.established_year == 2018
        assert updated.number_of_employees == 8
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_empty_website_url_stored_as_null(db, repos) -> None:
    user_id, merchant_id, _ = await _seed_merchant(db)
    try:
        created = await repos.merchant_business_command.create(
            _create(merchant_id, website_url="")
        )
        by_id = await repos.merchant_business_query.find_by_id(
            created.merchant_business_info_id
        )
        assert by_id.website_url is None
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_soft_delete_lifecycle(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_business_command.create(_create(merchant_id))
        business_id = created.merchant_business_info_id

        trashed = await repos.merchant_business_command.trash(business_id)
        assert trashed.deleted_at is not None

        listed = await repos.merchant_business_query.find_all(name, 1, 10)
        assert all(row.merchant_business_info_id != business_id for row in listed)
        active = await repos.merchant_business_query.find_active(name, 1, 10)
        assert all(row.merchant_business_info_id != business_id for row in active)
        trashed_rows = await repos.merchant_business_query.find_trashed(name, 1, 10)
        assert any(row.merchant_business_info_id == business_id for row in trashed_rows)

        with pytest.raises(AppError) as missing:
            await repos.merchant_business_query.find_by_id(business_id)
        assert missing.value.code == 404

        restored = await repos.merchant_business_command.restore(business_id)
        assert restored.deleted_at is None
        active_after = await repos.merchant_business_query.find_active(name, 1, 10)
        assert any(
            row.merchant_business_info_id == business_id for row in active_after
        )
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_find_all_ignores_merchant_deleted_but_find_active_does_not(
    db, repos
) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_business_command.create(_create(merchant_id))
        business_id = created.merchant_business_info_id

        # Trash the merchant (not the business info).
        await db.execute(
            "UPDATE merchants SET deleted_at = CURRENT_TIMESTAMP WHERE merchant_id = :mid",
            {"mid": merchant_id},
        )

        listed = await repos.merchant_business_query.find_all(name, 1, 10)
        assert any(
            row.merchant_business_info_id == business_id for row in listed
        )

        active = await repos.merchant_business_query.find_active(name, 1, 10)
        assert all(row.merchant_business_info_id != business_id for row in active)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_delete_permanent_requires_trashed(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_business_command.create(_create(merchant_id))
        business_id = created.merchant_business_info_id

        # A live row is not deleted (SQL guards deleted_at IS NOT NULL).
        await repos.merchant_business_command.delete_permanent(business_id)
        still_there = await repos.merchant_business_query.find_by_id(business_id)
        assert still_there.merchant_business_info_id == business_id

        await repos.merchant_business_command.trash(business_id)
        await repos.merchant_business_command.delete_permanent(business_id)
        trashed_rows = await repos.merchant_business_query.find_trashed(name, 1, 10)
        assert all(row.merchant_business_info_id != business_id for row in trashed_rows)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_missing_maps_to_not_found(db, repos) -> None:
    with pytest.raises(AppError) as excinfo:
        await repos.merchant_business_query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "merchant business not found"

    with pytest.raises(AppError) as trash_missing:
        await repos.merchant_business_command.trash(2_000_000_000)
    assert trash_missing.value.code == 404


async def test_pagination_reports_total_count(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        for _ in range(3):
            await repos.merchant_business_command.create(_create(merchant_id))
        rows = await repos.merchant_business_query.find_all(name, 1, 2)
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_restore_all_and_delete_all(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_business_command.create(_create(merchant_id))
        business_id = created.merchant_business_info_id
        await repos.merchant_business_command.trash(business_id)

        await repos.merchant_business_command.restore_all()
        active = await repos.merchant_business_query.find_active(name, 1, 10)
        assert any(row.merchant_business_info_id == business_id for row in active)

        await repos.merchant_business_command.trash(business_id)
        await repos.merchant_business_command.delete_all()
        trashed_rows = await repos.merchant_business_query.find_trashed(name, 1, 10)
        assert all(row.merchant_business_info_id != business_id for row in trashed_rows)
    finally:
        await _cleanup(db, user_id, merchant_id)


__all__ = []
