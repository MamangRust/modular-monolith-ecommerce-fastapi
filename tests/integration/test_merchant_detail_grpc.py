"""merchant_detail + merchant_social_link gRPC integration tests. Marked `integration`. Runs the three real merchant_detail servicers behind an ephemeral port, with the merchant adapter pointed at the real merchant server (the fixture spins that up too). Verifies the wire contract (`%Y-%m-%d %H:%M:%S.mmm` timestamps, the empty `social_media_links`, the `deleted_at` wrapper only on the `...DeleteAt` projections, the merchant envelopes for delete/restore-all) and the error mapping (400 guards survive as INVALID_ARGUMENT, a repository 404 stays NOT_FOUND, a failed merchant lookup becomes the adapter's 500)."""

from __future__ import annotations

import uuid

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.merchant import (
    merchant_command_pb2,
    merchant_command_pb2_grpc,
)
from pb.merchant_detail import (
    merchant_detail_command_pb2,
    merchant_detail_command_pb2_grpc,
    merchant_detail_common_pb2,
    merchant_detail_query_pb2,
    merchant_detail_query_pb2_grpc,
)
from pb.merchant_social_link import (
    merchant_social_link_command_pb2,
    merchant_social_link_command_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


async def _seed_user(db: Database) -> int:
    email = f"test_merchant_detail_grpc_{uuid.uuid4().hex[:10]}@example.com"
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


async def _cleanup(db: Database, merchant_id: int | None, user_id: int) -> None:
    if merchant_id is not None:
        await db.execute(
            "DELETE FROM merchant_social_media_links WHERE merchant_detail_id IN "
            "(SELECT merchant_detail_id FROM merchant_details WHERE merchant_id = :mid)",
            {"mid": merchant_id},
        )
        await db.execute(
            "DELETE FROM merchant_details WHERE merchant_id = :mid",
            {"mid": merchant_id},
        )
        await db.execute(
            "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
        )
    await db.execute("DELETE FROM outbox_events WHERE event_key LIKE 'merchant-%'")
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


async def test_merchant_detail_grpc_lifecycle(
    db: Database, merchant_grpc_server: str, merchant_detail_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_detail_grpc_server)
    merchant_channel = grpc.aio.insecure_channel(merchant_grpc_server)
    query = merchant_detail_query_pb2_grpc.MerchantDetailQueryServiceStub(channel)
    command = merchant_detail_command_pb2_grpc.MerchantDetailCommandServiceStub(channel)
    social = merchant_social_link_command_pb2_grpc.MerchantSocialCommandServiceStub(
        channel
    )
    merchant_command = merchant_command_pb2_grpc.MerchantCommandServiceStub(
        merchant_channel
    )

    user_id = await _seed_user(db)
    name = f"Merchant {uuid.uuid4().hex[:10]}"
    merchant_id: int | None = None

    try:
        merchant = await merchant_command.Create(
            merchant_command_pb2.CreateMerchantRequest(
                user_id=user_id,
                name=name,
                description="d",
                address="a",
                contact_email="e@f.com",
                contact_phone="0812",
                status="active",
            ),
            timeout=5,
        )
        merchant_id = merchant.data.id

        created = await command.Create(
            merchant_detail_command_pb2.CreateMerchantDetailRequest(
                merchant_id=merchant_id,
                display_name="Techno Store",
                cover_image_url="cover/techno.jpg",
                logo_url="logo/techno.png",
                short_description="Pusat elektronik",
                website_url="https://technostore.com",
            ),
            timeout=5,
        )
        assert created.message == "Successfully created merchant detail"
        assert created.data.merchant_id == merchant_id
        assert created.data.display_name == "Techno Store"
        # `%Y-%m-%d %H:%M:%S.mmm` = 23 chars.
        assert len(created.data.created_at) == 23
        detail_id = created.data.id

        found = await query.FindById(
            merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=detail_id),
            timeout=5,
        )
        assert found.message == "Successfully fetched merchant detail"
        assert found.data.id == detail_id
        # The wire list is always empty (ignores the column).
        assert len(found.data.social_media_links) == 0

        listed = await query.FindAll(
            merchant_detail_query_pb2.FindAllMerchantDetailRequest(
                page=1, page_size=10, search=name
            ),
            timeout=5,
        )
        assert listed.pagination.total_records >= 1

        link = await social.Create(
            merchant_social_link_command_pb2.CreateMerchantSocialRequest(
                merchant_detail_id=detail_id,
                platform="Facebook",
                url="https://facebook.com/merchant1",
            ),
            timeout=5,
        )
        assert link.message == "Successfully created merchant social link"
        assert link.data.merchant_detail_id == detail_id
        assert link.data.created_at  # the gRPC mapping fills it
        social_id = link.data.id

        updated_link = await social.Update(
            merchant_social_link_command_pb2.UpdateMerchantSocialRequest(
                id=social_id,
                merchant_detail_id=detail_id,
                platform="Twitter",
                url="https://twitter.com/merchant1",
            ),
            timeout=5,
        )
        assert updated_link.data.platform == "Twitter"

        trashed = await command.TrashedMerchantDetail(
            merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=detail_id),
            timeout=5,
        )
        assert trashed.message == "Successfully trashed merchant detail"
        assert trashed.data.deleted_at.value

        trashed_rows = await query.FindByTrashed(
            merchant_detail_query_pb2.FindAllMerchantDetailRequest(
                page=1, page_size=10, search=name
            ),
            timeout=5,
        )
        assert any(
            row.id == detail_id and row.deleted_at.value for row in trashed_rows.data
        )

        restored = await command.RestoreMerchantDetail(
            merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=detail_id),
            timeout=5,
        )
        assert restored.message == "Successfully restored merchant detail"

        updated = await command.Update(
            merchant_detail_command_pb2.UpdateMerchantDetailRequest(
                merchant_detail_id=detail_id,
                display_name="Techno Store v2",
                cover_image_url="c",
                logo_url="l",
                short_description="v2",
                website_url="https://v2.example.com",
            ),
            timeout=5,
        )
        assert updated.message == "Successfully updated merchant detail"
        assert updated.data.display_name == "Techno Store v2"

        # FindById guards id == 0 -> 400 invalid merchant detail ID.
        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await query.FindById(
                merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=0),
                timeout=5,
            )
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        parsed = parse_grpc_error(invalid.value)
        assert parsed.code == 400
        assert parsed.message == "invalid merchant detail ID"

        # A repository 404 is preserved as NOT_FOUND.
        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await command.TrashedMerchantDetail(
                merchant_detail_common_pb2.FindByIdMerchantDetailRequest(
                    id=2_000_000_000
                ),
                timeout=5,
            )
        assert missing.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing.value).code == 404

        # A failed merchant lookup is wrapped by the adapter into a 500.
        with pytest.raises(grpc.aio.AioRpcError) as bad_merchant:
            await command.Create(
                merchant_detail_command_pb2.CreateMerchantDetailRequest(
                    merchant_id=2_000_000_000,
                    display_name="X",
                    short_description="d",
                ),
                timeout=5,
            )
        assert bad_merchant.value.code() is grpc.StatusCode.INTERNAL
        assert parse_grpc_error(bad_merchant.value).code == 500

        await command.TrashedMerchantDetail(
            merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=detail_id),
            timeout=5,
        )
        deleted = await command.DeleteMerchantDetailPermanent(
            merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=detail_id),
            timeout=5,
        )
        # The delete response is the merchant envelope.
        assert deleted.message == "Successfully deleted merchant detail permanently"
    finally:
        await channel.close()
        await merchant_channel.close()
        await _cleanup(db, merchant_id, user_id)


async def test_merchant_detail_bulk_over_grpc(
    db: Database, merchant_grpc_server: str, merchant_detail_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_detail_grpc_server)
    merchant_channel = grpc.aio.insecure_channel(merchant_grpc_server)
    query = merchant_detail_query_pb2_grpc.MerchantDetailQueryServiceStub(channel)
    command = merchant_detail_command_pb2_grpc.MerchantDetailCommandServiceStub(channel)
    merchant_command = merchant_command_pb2_grpc.MerchantCommandServiceStub(
        merchant_channel
    )

    user_id = await _seed_user(db)
    name = f"Merchant {uuid.uuid4().hex[:10]}"
    merchant_id: int | None = None
    try:
        merchant = await merchant_command.Create(
            merchant_command_pb2.CreateMerchantRequest(
                user_id=user_id,
                name=name,
                description="d",
                address="a",
                contact_email="e@f.com",
                contact_phone="0812",
                status="active",
            ),
            timeout=5,
        )
        merchant_id = merchant.data.id

        created = await command.Create(
            merchant_detail_command_pb2.CreateMerchantDetailRequest(
                merchant_id=merchant_id,
                display_name="X",
                short_description="d",
            ),
            timeout=5,
        )
        detail_id = created.data.id

        await command.TrashedMerchantDetail(
            merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=detail_id),
            timeout=5,
        )
        restored_all = await command.RestoreAllMerchantDetail(
            empty_pb2.Empty(), timeout=5
        )
        assert restored_all.message == "Successfully restored all merchant details"

        active = await query.FindByActive(
            merchant_detail_query_pb2.FindAllMerchantDetailRequest(
                page=1, page_size=10, search=name
            ),
            timeout=5,
        )
        assert any(row.id == detail_id for row in active.data)

        await command.TrashedMerchantDetail(
            merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=detail_id),
            timeout=5,
        )
        deleted_all = await command.DeleteAllMerchantDetailPermanent(
            empty_pb2.Empty(), timeout=5
        )
        assert (
            deleted_all.message
            == "Successfully deleted all merchant details permanently"
        )
    finally:
        await channel.close()
        await merchant_channel.close()
        await _cleanup(db, merchant_id, user_id)


__all__ = []
