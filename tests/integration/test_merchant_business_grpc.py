"""merchant_business gRPC integration tests.

Marked `integration`. Runs the two real merchant_business servicers behind an
ephemeral port. The merchant adapter is wired but never invoked, so tests seed
the parent merchant directly in the DB.

Verifies the wire contract (`.mmm` timestamps — no DATE columns here, the
`deleted_at` wrapper only on the `...DeleteAt` projections, the merchant
envelopes for delete/restore-all, the never-filled `merchant_name`) and the
error mapping:
- `FindById id == 0` -> 400 `Invalid merchant business ID` (unlike merchant_award,
  which returns a generic 500);
- a repository 404 stays NOT_FOUND;
- a failed create (FK violation) is remapped to the service's 500 sentinel.
"""

from __future__ import annotations

import uuid

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.merchant import merchant_query_pb2
from pb.merchant_business import (
    merchant_business_command_pb2,
    merchant_business_command_pb2_grpc,
    merchant_business_common_pb2,
    merchant_business_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


async def _seed_merchant(db: Database) -> tuple[int, int, str]:
    email = f"test_merchant_business_grpc_{uuid.uuid4().hex[:10]}@example.com"
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
        "DELETE FROM merchant_business_information WHERE merchant_id = :mid",
        {"mid": merchant_id},
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


async def test_merchant_business_grpc_lifecycle(
    db: Database, merchant_business_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_business_grpc_server)
    query = merchant_business_query_pb2_grpc.MerchantBusinessQueryServiceStub(
        channel
    )
    command = merchant_business_command_pb2_grpc.MerchantBusinessCommandServiceStub(
        channel
    )

    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await command.Create(
            merchant_business_command_pb2.CreateMerchantBusinessRequest(
                merchant_id=merchant_id,
                business_type="Toko Elektronik",
                tax_id="01.234.567.8-999.000",
                established_year=2010,
                number_of_employees=15,
                website_url="https://technostore.com",
            ),
            timeout=5,
        )
        assert created.message == "Successfully created merchant business"
        assert created.data.merchant_id == merchant_id
        assert created.data.business_type == "Toko Elektronik"
        assert created.data.established_year == 2010
        # `%Y-%m-%d %H:%M:%S.mmm` = 23 chars.
        assert len(created.data.created_at) == 23
        # merchant_name is never projected.
        assert created.data.merchant_name == ""
        business_id = created.data.id

        found = await query.FindById(
            merchant_business_common_pb2.FindByIdMerchantBusinessRequest(
                id=business_id
            ),
            timeout=5,
        )
        assert found.message == "Successfully fetched merchant"
        assert found.data.id == business_id

        listed = await query.FindAll(
            merchant_query_pb2.FindAllMerchantRequest(
                page=1, page_size=10, search=name
            ),
            timeout=5,
        )
        assert listed.pagination.total_records >= 1
        assert any(row.id == business_id for row in listed.data)

        trashed = await command.TrashedMerchantBusiness(
            merchant_business_common_pb2.FindByIdMerchantBusinessRequest(
                id=business_id
            ),
            timeout=5,
        )
        assert trashed.message == "Successfully trashed merchant business"
        assert trashed.data.deleted_at.value

        trashed_rows = await query.FindByTrashed(
            merchant_query_pb2.FindAllMerchantRequest(
                page=1, page_size=10, search=name
            ),
            timeout=5,
        )
        assert any(
            row.id == business_id and row.deleted_at.value for row in trashed_rows.data
        )

        restored = await command.RestoreMerchantBusiness(
            merchant_business_common_pb2.FindByIdMerchantBusinessRequest(
                id=business_id
            ),
            timeout=5,
        )
        assert restored.message == "Successfully restored merchant business"

        updated = await command.Update(
            merchant_business_command_pb2.UpdateMerchantBusinessRequest(
                merchant_business_info_id=business_id,
                business_type="Retail Gadget",
                tax_id="04.567.890.1-666.000",
                established_year=2018,
                number_of_employees=8,
                website_url="",
            ),
            timeout=5,
        )
        assert updated.message == "Successfully updated merchant business"
        assert updated.data.business_type == "Retail Gadget"
        assert updated.data.established_year == 2018
        # Empty optionals come back as "".
        assert updated.data.website_url == ""

        # FindById guards id == 0 with a dedicated 400 (unlike merchant_award).
        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await query.FindById(
                merchant_business_common_pb2.FindByIdMerchantBusinessRequest(id=0),
                timeout=5,
            )
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        parsed = parse_grpc_error(invalid.value)
        assert parsed.code == 400
        assert parsed.message == "Invalid merchant business ID"

        # A repository 404 is preserved as NOT_FOUND.
        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await command.TrashedMerchantBusiness(
                merchant_business_common_pb2.FindByIdMerchantBusinessRequest(
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
                merchant_business_command_pb2.CreateMerchantBusinessRequest(
                    merchant_id=2_000_000_000,
                    business_type="X",
                    tax_id="t",
                    established_year=2010,
                    number_of_employees=1,
                ),
                timeout=5,
            )
        assert bad_create.value.code() is grpc.StatusCode.INTERNAL
        assert parse_grpc_error(bad_create.value).message == (
            "Failed to create merchant business"
        )

        await command.TrashedMerchantBusiness(
            merchant_business_common_pb2.FindByIdMerchantBusinessRequest(
                id=business_id
            ),
            timeout=5,
        )
        deleted = await command.DeleteMerchantBusinessPermanent(
            merchant_business_common_pb2.FindByIdMerchantBusinessRequest(
                id=business_id
            ),
            timeout=5,
        )
        assert deleted.message == "Successfully deleted merchant business permanently"
    finally:
        await channel.close()
        await _cleanup(db, merchant_id, user_id)


async def test_merchant_business_bulk_over_grpc(
    db: Database, merchant_business_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_business_grpc_server)
    query = merchant_business_query_pb2_grpc.MerchantBusinessQueryServiceStub(
        channel
    )
    command = merchant_business_command_pb2_grpc.MerchantBusinessCommandServiceStub(
        channel
    )

    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await command.Create(
            merchant_business_command_pb2.CreateMerchantBusinessRequest(
                merchant_id=merchant_id,
                business_type="Toko Elektronik",
                tax_id="t",
                established_year=2010,
                number_of_employees=1,
            ),
            timeout=5,
        )
        business_id = created.data.id

        await command.TrashedMerchantBusiness(
            merchant_business_common_pb2.FindByIdMerchantBusinessRequest(
                id=business_id
            ),
            timeout=5,
        )
        restored_all = await command.RestoreAllMerchantBusiness(
            empty_pb2.Empty(), timeout=5
        )
        assert (
            restored_all.message
            == "Successfully restored all trashed merchant businesses"
        )

        active = await query.FindByActive(
            merchant_query_pb2.FindAllMerchantRequest(
                page=1, page_size=10, search=name
            ),
            timeout=5,
        )
        assert any(row.id == business_id for row in active.data)

        await command.TrashedMerchantBusiness(
            merchant_business_common_pb2.FindByIdMerchantBusinessRequest(
                id=business_id
            ),
            timeout=5,
        )
        deleted_all = await command.DeleteAllMerchantBusinessPermanent(
            empty_pb2.Empty(), timeout=5
        )
        assert (
            deleted_all.message
            == "Successfully deleted all merchant businesses permanently"
        )
    finally:
        await channel.close()
        await _cleanup(db, merchant_id, user_id)


__all__ = []
