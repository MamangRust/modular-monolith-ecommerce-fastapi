"""merchant_award gRPC integration tests.

Marked `integration`. Runs the two real merchant_award servicers behind an
ephemeral port. The merchant adapter is wired but never invoked, so tests seed
the parent merchant directly in the DB."""

from __future__ import annotations

import uuid

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.merchant import merchant_query_pb2
from pb.merchant_award import (
    merchant_award_command_pb2,
    merchant_award_command_pb2_grpc,
    merchant_award_common_pb2,
    merchant_award_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


async def _seed_merchant(db: Database) -> tuple[int, int, str]:
    email = f"test_merchant_award_grpc_{uuid.uuid4().hex[:10]}@example.com"
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


async def _cleanup(db: Database, merchant_id: int, user_id: int) -> None:
    await db.execute(
        "DELETE FROM merchant_certifications_and_awards WHERE merchant_id = :mid",
        {"mid": merchant_id},
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


async def test_merchant_award_grpc_lifecycle(
    db: Database, merchant_award_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_award_grpc_server)
    query = merchant_award_query_pb2_grpc.MerchantAwardQueryServiceStub(channel)
    command = merchant_award_command_pb2_grpc.MerchantAwardCommandServiceStub(channel)

    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await command.Create(
            merchant_award_command_pb2.CreateMerchantAwardRequest(
                merchant_id=merchant_id,
                title="ISO 9001",
                description="Quality management",
                issued_by="BSN",
                issue_date="2026-01-02",
                expiry_date="2027-01-02",
                certificate_url="https://certs.example.com/1",
            ),
            timeout=5,
        )
        assert created.message == "Successfully created merchant award"
        assert created.data.merchant_id == merchant_id
        assert created.data.title == "ISO 9001"
        assert created.data.issue_date == "2026-01-02"
        assert created.data.expiry_date == "2027-01-02"
        # `%Y-%m-%d %H:%M:%S.mmm` = 23 chars.
        assert len(created.data.created_at) == 23
        # merchant_name is never projected.
        assert created.data.merchant_name == ""
        award_id = created.data.id

        found = await query.FindById(
            merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=award_id),
            timeout=5,
        )
        assert found.message == "Successfully fetched merchant"
        assert found.data.id == award_id

        listed = await query.FindAll(
            merchant_query_pb2.FindAllMerchantRequest(
                page=1, page_size=10, search=name
            ),
            timeout=5,
        )
        assert listed.pagination.total_records >= 1
        assert any(row.id == award_id for row in listed.data)

        trashed = await command.TrashedMerchantAward(
            merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=award_id),
            timeout=5,
        )
        assert trashed.message == "Successfully trashed merchant award"
        assert trashed.data.deleted_at.value

        trashed_rows = await query.FindByTrashed(
            merchant_query_pb2.FindAllMerchantRequest(
                page=1, page_size=10, search=name
            ),
            timeout=5,
        )
        assert any(
            row.id == award_id and row.deleted_at.value for row in trashed_rows.data
        )

        restored = await command.RestoreMerchantAward(
            merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=award_id),
            timeout=5,
        )
        assert restored.message == "Successfully restored merchant award"

        updated = await command.Update(
            merchant_award_command_pb2.UpdateMerchantAwardRequest(
                merchant_certification_id=award_id,
                title="ISO 9001 v2",
                description="v2",
                issued_by="BSN",
                issue_date="2026-02-03",
                expiry_date="",
                certificate_url="",
            ),
            timeout=5,
        )
        assert updated.message == "Successfully updated merchant award"
        assert updated.data.title == "ISO 9001 v2"
        assert updated.data.issue_date == "2026-02-03"
        # Empty optionals come back as "".
        assert updated.data.expiry_date == ""

        # FindById guards id == 0 with a generic 500 (NOT a 400).
        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await query.FindById(
                merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=0),
                timeout=5,
            )
        assert invalid.value.code() is grpc.StatusCode.INTERNAL
        parsed = parse_grpc_error(invalid.value)
        assert parsed.code == 500
        assert parsed.message == "Internal server error"

        # A repository 404 is preserved as NOT_FOUND.
        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await command.TrashedMerchantAward(
                merchant_award_common_pb2.FindByIdMerchantAwardRequest(
                    id=2_000_000_000
                ),
                timeout=5,
            )
        assert missing.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing.value).code == 404

        # A create for a non-existent merchant violates the FK; the repository
        # 500 is remapped by the service to its own 500 sentinel.
        with pytest.raises(grpc.aio.AioRpcError) as bad_create:
            await command.Create(
                merchant_award_command_pb2.CreateMerchantAwardRequest(
                    merchant_id=2_000_000_000,
                    title="X",
                    description="d",
                    issued_by="BSN",
                    issue_date="2026-01-02",
                ),
                timeout=5,
            )
        assert bad_create.value.code() is grpc.StatusCode.INTERNAL
        assert parse_grpc_error(bad_create.value).message == (
            "Failed to create merchant award"
        )

        await command.TrashedMerchantAward(
            merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=award_id),
            timeout=5,
        )
        deleted = await command.DeleteMerchantAwardPermanent(
            merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=award_id),
            timeout=5,
        )
        assert deleted.message == "Successfully deleted merchant award permanently"
    finally:
        await channel.close()
        await _cleanup(db, merchant_id, user_id)


async def test_merchant_award_bulk_over_grpc(
    db: Database, merchant_award_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_award_grpc_server)
    query = merchant_award_query_pb2_grpc.MerchantAwardQueryServiceStub(channel)
    command = merchant_award_command_pb2_grpc.MerchantAwardCommandServiceStub(channel)

    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await command.Create(
            merchant_award_command_pb2.CreateMerchantAwardRequest(
                merchant_id=merchant_id,
                title="ISO 9001",
                description="d",
                issued_by="BSN",
                issue_date="2026-01-02",
            ),
            timeout=5,
        )
        award_id = created.data.id

        await command.TrashedMerchantAward(
            merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=award_id),
            timeout=5,
        )
        restored_all = await command.RestoreAllMerchantAward(
            empty_pb2.Empty(), timeout=5
        )
        assert restored_all.message == "Successfully restored all trashed merchant awards"

        active = await query.FindByActive(
            merchant_query_pb2.FindAllMerchantRequest(
                page=1, page_size=10, search=name
            ),
            timeout=5,
        )
        assert any(row.id == award_id for row in active.data)

        await command.TrashedMerchantAward(
            merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=award_id),
            timeout=5,
        )
        deleted_all = await command.DeleteAllMerchantAwardPermanent(
            empty_pb2.Empty(), timeout=5
        )
        assert (
            deleted_all.message
            == "Successfully deleted all merchant awards permanently"
        )
    finally:
        await channel.close()
        await _cleanup(db, merchant_id, user_id)


__all__ = []
