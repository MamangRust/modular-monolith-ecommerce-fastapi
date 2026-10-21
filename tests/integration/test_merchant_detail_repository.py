"""merchant_detail + merchant_social_link repository integration tests.

Marked `integration` (excluded from `make test`). `merchant_details.merchant_id`
has a `REFERENCES merchants(merchant_id)` FK and `merchants.user_id` references
`users`, so each test seeds its own user + merchant and removes them afterwards
(the FK cascades clean the detail + social rows). A unique merchant name is used
as the search key (`find_all`/`find_active`/`find_trashed` search `m.name`).

:
- `find_all` filters `md.deleted_at IS NULL` but NOT `m.deleted_at`, while
 `find_active` additionally requires `m.deleted_at IS NULL`;
- `find_trashed` filters `md.deleted_at IS NOT NULL`;
- `find_by_id` adds `AND md.deleted_at IS NULL`;
- `delete_permanent` only affects trashed rows (`deleted_at IS NOT NULL`)."""

from __future__ import annotations

import uuid

import grpc
import pytest

from service.merchant_detail.repository import GuardOptions, new_repositories
from shared.domain.requests.merchant_detail import (
    CreateMerchantDetailRequest,
    CreateMerchantSocialRequest,
    UpdateMerchantDetailRequest,
    UpdateMerchantSocialRequest,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


@pytest.fixture
async def repos(db):
    """merchant_detail repositories with an unused merchant channel."""
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    try:
        yield new_repositories(db, merchant_channel=channel, guards=GuardOptions())
    finally:
        await channel.close()


async def _seed_merchant(db) -> tuple[int, int, str]:
    email = f"test_merchant_detail_{uuid.uuid4().hex[:10]}@example.com"
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
        "DELETE FROM merchant_social_media_links WHERE merchant_detail_id IN "
        "(SELECT merchant_detail_id FROM merchant_details WHERE merchant_id = :mid)",
        {"mid": merchant_id},
    )
    await db.execute(
        "DELETE FROM merchant_details WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


def _create(merchant_id: int) -> CreateMerchantDetailRequest:
    return CreateMerchantDetailRequest(
        merchant_id=merchant_id,
        display_name="Techno Store",
        cover_image_url="cover/techno.jpg",
        logo_url="logo/techno.png",
        short_description="Pusat elektronik",
        website_url="https://technostore.com",
    )


async def test_create_and_find(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_detail_command.create(_create(merchant_id))
        assert created.merchant_detail_id > 0
        assert created.display_name == "Techno Store"

        by_id = await repos.merchant_detail_query.find_by_id(
            created.merchant_detail_id
        )
        assert by_id.merchant_detail_id == created.merchant_detail_id
        assert by_id.merchant_name == name

        listed = await repos.merchant_detail_query.find_all(name, 1, 10)
        assert any(
            row.merchant_detail_id == created.merchant_detail_id for row in listed
        )
        assert listed[0].total_count >= 1
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_update_changes_fields(db, repos) -> None:
    user_id, merchant_id, _ = await _seed_merchant(db)
    try:
        created = await repos.merchant_detail_command.create(_create(merchant_id))
        updated = await repos.merchant_detail_command.update(
            UpdateMerchantDetailRequest(
                merchant_detail_id=created.merchant_detail_id,
                display_name="Techno Store v2",
                cover_image_url="cover/v2.jpg",
                logo_url="logo/v2.png",
                short_description="v2",
                website_url="https://v2.example.com",
            )
        )
        assert updated.display_name == "Techno Store v2"
        assert updated.website_url == "https://v2.example.com"
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_soft_delete_lifecycle(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_detail_command.create(_create(merchant_id))
        detail_id = created.merchant_detail_id

        trashed = await repos.merchant_detail_command.trash(detail_id)
        assert trashed.deleted_at is not None

        listed = await repos.merchant_detail_query.find_all(name, 1, 10)
        assert all(row.merchant_detail_id != detail_id for row in listed)
        active = await repos.merchant_detail_query.find_active(name, 1, 10)
        assert all(row.merchant_detail_id != detail_id for row in active)
        trashed_rows = await repos.merchant_detail_query.find_trashed(name, 1, 10)
        assert any(row.merchant_detail_id == detail_id for row in trashed_rows)

        with pytest.raises(AppError) as missing:
            await repos.merchant_detail_query.find_by_id(detail_id)
        assert missing.value.code == 404

        restored = await repos.merchant_detail_command.restore(detail_id)
        assert restored.deleted_at is None
        active_after = await repos.merchant_detail_query.find_active(name, 1, 10)
        assert any(row.merchant_detail_id == detail_id for row in active_after)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_find_all_ignores_merchant_deleted_but_find_active_does_not(
    db, repos
) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_detail_command.create(_create(merchant_id))
        detail_id = created.merchant_detail_id

        # Trash the merchant (not the detail).
        await db.execute(
            "UPDATE merchants SET deleted_at = CURRENT_TIMESTAMP WHERE merchant_id = :mid",
            {"mid": merchant_id},
        )

        listed = await repos.merchant_detail_query.find_all(name, 1, 10)
        assert any(row.merchant_detail_id == detail_id for row in listed)

        active = await repos.merchant_detail_query.find_active(name, 1, 10)
        assert all(row.merchant_detail_id != detail_id for row in active)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_delete_permanent_requires_trashed(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_detail_command.create(_create(merchant_id))
        detail_id = created.merchant_detail_id

        # A live row is not deleted (SQL guards deleted_at IS NOT NULL).
        await repos.merchant_detail_command.delete_permanent(detail_id)
        still_there = await repos.merchant_detail_query.find_by_id(detail_id)
        assert still_there.merchant_detail_id == detail_id

        await repos.merchant_detail_command.trash(detail_id)
        await repos.merchant_detail_command.delete_permanent(detail_id)
        trashed_rows = await repos.merchant_detail_query.find_trashed(name, 1, 10)
        assert all(row.merchant_detail_id != detail_id for row in trashed_rows)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_missing_maps_to_not_found(db, repos) -> None:
    with pytest.raises(AppError) as excinfo:
        await repos.merchant_detail_query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "merchant detail not found"

    with pytest.raises(AppError) as trash_missing:
        await repos.merchant_detail_command.trash(2_000_000_000)
    assert trash_missing.value.code == 404


async def test_pagination_reports_total_count(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    ids: list[int] = []
    try:
        for _ in range(3):
            row = await repos.merchant_detail_command.create(_create(merchant_id))
            ids.append(row.merchant_detail_id)
        rows = await repos.merchant_detail_query.find_all(name, 1, 2)
        assert len(rows) == 2
        assert rows[0].total_count >= 3
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_restore_all_and_delete_all(db, repos) -> None:
    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await repos.merchant_detail_command.create(_create(merchant_id))
        detail_id = created.merchant_detail_id
        await repos.merchant_detail_command.trash(detail_id)

        await repos.merchant_detail_command.restore_all()
        active = await repos.merchant_detail_query.find_active(name, 1, 10)
        assert any(row.merchant_detail_id == detail_id for row in active)

        await repos.merchant_detail_command.trash(detail_id)
        await repos.merchant_detail_command.delete_all()
        trashed_rows = await repos.merchant_detail_query.find_trashed(name, 1, 10)
        assert all(row.merchant_detail_id != detail_id for row in trashed_rows)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_social_media_links_aggregate(db, repos) -> None:
    user_id, merchant_id, _ = await _seed_merchant(db)
    try:
        created = await repos.merchant_detail_command.create(_create(merchant_id))
        detail_id = created.merchant_detail_id

        for platform in ("Facebook", "Instagram", "Twitter"):
            await repos.merchant_social_link_command.create(
                CreateMerchantSocialRequest(
                    merchant_detail_id=detail_id,
                    platform=platform,
                    url=f"https://{platform.lower()}.com/merchant1",
                )
            )

        by_id = await repos.merchant_detail_query.find_by_id(detail_id)
        links = by_id.social_media_links
        # asyncpg decodes the json_agg column to a Python list.
        assert isinstance(links, list)
        assert len(links) == 3
        platforms = {link["platform"] for link in links}
        assert platforms == {"Facebook", "Instagram", "Twitter"}
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_social_link_lifecycle(db, repos) -> None:
    user_id, merchant_id, _ = await _seed_merchant(db)
    try:
        created = await repos.merchant_detail_command.create(_create(merchant_id))
        detail_id = created.merchant_detail_id

        link = await repos.merchant_social_link_command.create(
            CreateMerchantSocialRequest(
                merchant_detail_id=detail_id,
                platform="Facebook",
                url="https://facebook.com/merchant1",
            )
        )
        social_id = link.merchant_social_id
        assert social_id > 0

        updated = await repos.merchant_social_link_command.update(
            UpdateMerchantSocialRequest(
                id=social_id,
                merchant_detail_id=detail_id,
                platform="Twitter",
                url="https://twitter.com/merchant1",
            )
        )
        assert updated.platform == "Twitter"

        # Trash/restore carry RETURNING, so a missing row is NOT_FOUND.
        assert await repos.merchant_social_link_command.trash(social_id) is True
        with pytest.raises(AppError) as missing:
            await repos.merchant_social_link_command.trash(social_id)
        assert missing.value.code == 404

        assert await repos.merchant_social_link_command.restore(social_id) is True

        assert await repos.merchant_social_link_command.delete_permanent(social_id)
        # delete_permanent is :exec, so a second call still reports success.
        assert await repos.merchant_social_link_command.delete_permanent(social_id)

        # Bulk ops ignore affected rows and always succeed.
        assert await repos.merchant_social_link_command.restore_all()
        assert await repos.merchant_social_link_command.delete_all()
    finally:
        await _cleanup(db, user_id, merchant_id)


__all__ = []
