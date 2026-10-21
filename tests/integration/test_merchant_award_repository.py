"""merchant_award repository integration tests. Marked `integration` (excluded from `make test`). `merchant_certifications_and_awards.merchant_id` has a `REFERENCES merchants(merchant_id) ON DELETE CASCADE` FK, so each test seeds its own user + merchant and removes them afterwards. A unique merchant name is used as the search key (`find_all`/`find_active`/`find_trashed` search `m.name`).: - `find_all` filters `mca.deleted_at IS NULL` but NOT `m.deleted_at`, while `find_active` additionally requires `m.deleted_at IS NULL`; - `find_trashed` filters `mca.deleted_at IS NOT NULL`; - `find_by_id` adds `AND deleted_at IS NULL` and maps a missing row to 404; - `delete_permanent` only affects trashed rows (`deleted_at IS NOT NULL`); - empty `certificate_url`/`expiry_date` are stored as NULL (`stringPtr` / `parseDateToPgDate`)."""

from __future__ import annotations

import uuid
from datetime import date

import grpc
import pytest

from service.merchant_award.repository import GuardOptions, new_repositories
from shared.domain.requests.merchant_award import (
    CreateMerchantCertificationOrAwardRequest,
    UpdateMerchantCertificationOrAwardRequest,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


@pytest.fixture
async def repos(db):
    """merchant_award repositories with an unused merchant channel."""
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    try:
        yield new_repositories(db, merchant_channel=channel, guards=GuardOptions())
    finally:
        await channel.close()


async def _seed_merchant(db) -> tuple[int, int, str]:
    email = f"test_merchant_award_{uuid.uuid4().hex[:10]}@example.com"
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
        "DELETE FROM merchant_certifications_and_awards WHERE merchant_id = :mid",
        {"mid": merchant_id},
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


def _create(merchant_id: int, **overrides) -> CreateMerchantCertificationOrAwardRequest:
    values = {
        "merchant_id": merchant_id,
        "title": "ISO 9001",
        "description": "Quality management",
        "issued_by": "BSN",
        "issue_date": "2026-01-02",
        "expiry_date": "2027-01-02",
        "certificate_url": "https://certs.example.com/1",
    }
    values.update(overrides)
    return CreateMerchantCertificationOrAwardRequest(**values)


async def test_create_and_find(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_award_command.create(_create(merchant_id))
        assert created.merchant_certification_id > 0
        assert created.title == "ISO 9001"
        # DATE columns decode to `datetime.date`.
        assert created.issue_date == date(2026, 1, 2)
        assert created.expiry_date == date(2027, 1, 2)

        by_id = await repos.merchant_award_query.find_by_id(
            created.merchant_certification_id
        )
        assert by_id.merchant_certification_id == created.merchant_certification_id

        listed = await repos.merchant_award_query.find_all(name, 1, 10)
        assert any(
            row.merchant_certification_id == created.merchant_certification_id
            for row in listed
        )
        assert listed[0].total_count >= 1
        assert listed[0].merchant_name == name
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_update_changes_fields(db, repos) -> None:
    user_id, merchant_id, _ = await _seed_merchant(db)
    try:
        created = await repos.merchant_award_command.create(_create(merchant_id))
        updated = await repos.merchant_award_command.update(
            UpdateMerchantCertificationOrAwardRequest(
                merchant_certification_id=created.merchant_certification_id,
                title="ISO 9001 v2",
                description="v2",
                issued_by="BSN v2",
                issue_date="2026-02-03",
                expiry_date="",
                certificate_url="https://certs.example.com/2",
            )
        )
        assert updated.title == "ISO 9001 v2"
        assert updated.issued_by == "BSN v2"
        assert updated.issue_date == date(2026, 2, 3)
        assert updated.expiry_date is None
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_empty_optionals_stored_as_null(db, repos) -> None:
    user_id, merchant_id, _ = await _seed_merchant(db)
    try:
        created = await repos.merchant_award_command.create(
            _create(merchant_id, expiry_date="", certificate_url="")
        )
        by_id = await repos.merchant_award_query.find_by_id(
            created.merchant_certification_id
        )
        assert by_id.expiry_date is None
        assert by_id.certificate_url is None
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_soft_delete_lifecycle(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_award_command.create(_create(merchant_id))
        award_id = created.merchant_certification_id

        trashed = await repos.merchant_award_command.trash(award_id)
        assert trashed.deleted_at is not None

        listed = await repos.merchant_award_query.find_all(name, 1, 10)
        assert all(row.merchant_certification_id != award_id for row in listed)
        active = await repos.merchant_award_query.find_active(name, 1, 10)
        assert all(row.merchant_certification_id != award_id for row in active)
        trashed_rows = await repos.merchant_award_query.find_trashed(name, 1, 10)
        assert any(row.merchant_certification_id == award_id for row in trashed_rows)

        with pytest.raises(AppError) as missing:
            await repos.merchant_award_query.find_by_id(award_id)
        assert missing.value.code == 404

        restored = await repos.merchant_award_command.restore(award_id)
        assert restored.deleted_at is None
        active_after = await repos.merchant_award_query.find_active(name, 1, 10)
        assert any(row.merchant_certification_id == award_id for row in active_after)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_find_all_ignores_merchant_deleted_but_find_active_does_not(
    db, repos
) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_award_command.create(_create(merchant_id))
        award_id = created.merchant_certification_id

        # Trash the merchant (not the award).
        await db.execute(
            "UPDATE merchants SET deleted_at = CURRENT_TIMESTAMP WHERE merchant_id = :mid",
            {"mid": merchant_id},
        )

        listed = await repos.merchant_award_query.find_all(name, 1, 10)
        assert any(row.merchant_certification_id == award_id for row in listed)

        active = await repos.merchant_award_query.find_active(name, 1, 10)
        assert all(row.merchant_certification_id != award_id for row in active)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_delete_permanent_requires_trashed(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_award_command.create(_create(merchant_id))
        award_id = created.merchant_certification_id

        # A live row is not deleted (SQL guards deleted_at IS NOT NULL).
        await repos.merchant_award_command.delete_permanent(award_id)
        still_there = await repos.merchant_award_query.find_by_id(award_id)
        assert still_there.merchant_certification_id == award_id

        await repos.merchant_award_command.trash(award_id)
        await repos.merchant_award_command.delete_permanent(award_id)
        trashed_rows = await repos.merchant_award_query.find_trashed(name, 1, 10)
        assert all(row.merchant_certification_id != award_id for row in trashed_rows)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_missing_maps_to_not_found(db, repos) -> None:
    with pytest.raises(AppError) as excinfo:
        await repos.merchant_award_query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "merchant award not found"

    with pytest.raises(AppError) as trash_missing:
        await repos.merchant_award_command.trash(2_000_000_000)
    assert trash_missing.value.code == 404


async def test_pagination_reports_total_count(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        for _ in range(3):
            await repos.merchant_award_command.create(_create(merchant_id))
        rows = await repos.merchant_award_query.find_all(name, 1, 2)
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_restore_all_and_delete_all(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_award_command.create(_create(merchant_id))
        award_id = created.merchant_certification_id
        await repos.merchant_award_command.trash(award_id)

        await repos.merchant_award_command.restore_all()
        active = await repos.merchant_award_query.find_active(name, 1, 10)
        assert any(row.merchant_certification_id == award_id for row in active)

        await repos.merchant_award_command.trash(award_id)
        await repos.merchant_award_command.delete_all()
        trashed_rows = await repos.merchant_award_query.find_trashed(name, 1, 10)
        assert all(row.merchant_certification_id != award_id for row in trashed_rows)
    finally:
        await _cleanup(db, user_id, merchant_id)


__all__ = []
