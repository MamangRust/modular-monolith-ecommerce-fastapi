"""merchant_policy gRPC integration tests. Marked `integration`. Runs the two real merchant_policy servicers behind an ephemeral port. The merchant adapter is wired but never invoked, so tests seed the parent merchant directly in the DB. Verifies the wire contract (`.mmm` timestamps, the `deleted_at` wrapper only on the `...DeleteAt` projections, the merchant envelopes for delete/restore-all, and the filled `merchant_name` on list rows) and the error mapping: - `FindById id == 0` -> 400 `invalid merchant policy id` (a port addition; the handler had no guard); - a repository 404 stays NOT_FOUND; - a failed create (FK violation) is remapped to the service's 500 sentinel."""

from __future__ import annotations

import uuid

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.merchant import merchant_query_pb2
from pb.merchant_policy import (
    merchant_policy_command_pb2,
    merchant_policy_command_pb2_grpc,
    merchant_policy_common_pb2,
    merchant_policy_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


async def _seed_merchant(db: Database) -> tuple[int, int, str]:
    email = f"test_merchant_policy_grpc_{uuid.uuid4().hex[:10]}@example.com"
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
        "DELETE FROM merchant_policies WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :mid", {"mid": merchant_id}
    )
    await db.execute("DELETE FROM users WHERE user_id = :uid", {"uid": user_id})


async def test_merchant_policy_grpc_lifecycle(
    db: Database, merchant_policy_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_policy_grpc_server)
    query = merchant_policy_query_pb2_grpc.MerchantPolicyQueryServiceStub(channel)
    command = merchant_policy_command_pb2_grpc.MerchantPolicyCommandServiceStub(channel)

    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await command.Create(
            merchant_policy_command_pb2.CreateMerchantPoliciesRequest(
                merchant_id=merchant_id,
                policy_type="Shipping",
                title="Free Shipping on Orders Above $50",
                description="desc",
            ),
            timeout=5,
        )
        assert created.message == "Successfully created merchant policy"
        assert created.data.merchant_id == merchant_id
        assert created.data.policy_type == "Shipping"
        assert len(created.data.created_at) == 23
        policy_id = created.data.id

        found = await query.FindById(
            merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=policy_id),
            timeout=5,
        )
        assert found.message == "Successfully fetched merchant policy"
        assert found.data.id == policy_id

        listed = await query.FindAll(
            merchant_query_pb2.FindAllMerchantRequest(
                page=1, page_size=10, search=name
            ),
            timeout=5,
        )
        assert listed.pagination.total_records >= 1
        row = next(r for r in listed.data if r.id == policy_id)
        # Unlike merchant_business, merchant_name IS projected for list rows.
        assert row.merchant_name == name

        trashed = await command.TrashedMerchantPolicies(
            merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=policy_id),
            timeout=5,
        )
        assert trashed.message == "Successfully processed merchant policy"
        assert trashed.data.deleted_at.value

        trashed_rows = await query.FindByTrashed(
            merchant_query_pb2.FindAllMerchantRequest(
                page=1, page_size=10, search=name
            ),
            timeout=5,
        )
        assert any(
            r.id == policy_id and r.deleted_at.value for r in trashed_rows.data
        )

        restored = await command.RestoreMerchantPolicies(
            merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=policy_id),
            timeout=5,
        )
        assert restored.message == "Successfully processed merchant policy"

        updated = await command.Update(
            merchant_policy_command_pb2.UpdateMerchantPoliciesRequest(
                merchant_policy_id=policy_id,
                policy_type="Refund",
                title="30-Day Refund Policy",
                description="updated",
            ),
            timeout=5,
        )
        assert updated.message == "Successfully updated merchant policy"
        assert updated.data.policy_type == "Refund"

        # FindById guards id == 0 with a dedicated 400 (a port addition).
        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await query.FindById(
                merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=0),
                timeout=5,
            )
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        parsed = parse_grpc_error(invalid.value)
        assert parsed.code == 400
        assert parsed.message == "invalid merchant policy id"

        # A repository 404 is preserved as NOT_FOUND.
        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await command.TrashedMerchantPolicies(
                merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(
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
                merchant_policy_command_pb2.CreateMerchantPoliciesRequest(
                    merchant_id=2_000_000_000,
                    policy_type="Shipping",
                    title="t",
                    description="d",
                ),
                timeout=5,
            )
        assert bad_create.value.code() is grpc.StatusCode.INTERNAL
        assert parse_grpc_error(bad_create.value).message == (
            "failed to create merchant policy"
        )

        await command.TrashedMerchantPolicies(
            merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=policy_id),
            timeout=5,
        )
        deleted = await command.DeleteMerchantPoliciesPermanent(
            merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=policy_id),
            timeout=5,
        )
        assert deleted.message == "Successfully deleted merchant policy permanently"
    finally:
        await channel.close()
        await _cleanup(db, merchant_id, user_id)


async def test_merchant_policy_bulk_over_grpc(
    db: Database, merchant_policy_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_policy_grpc_server)
    query = merchant_policy_query_pb2_grpc.MerchantPolicyQueryServiceStub(channel)
    command = merchant_policy_command_pb2_grpc.MerchantPolicyCommandServiceStub(channel)

    user_id, merchant_id, name = await _seed_merchant(db)
    try:
        created = await command.Create(
            merchant_policy_command_pb2.CreateMerchantPoliciesRequest(
                merchant_id=merchant_id,
                policy_type="Shipping",
                title="Free Shipping",
                description="d",
            ),
            timeout=5,
        )
        policy_id = created.data.id

        await command.TrashedMerchantPolicies(
            merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=policy_id),
            timeout=5,
        )
        restored_all = await command.RestoreAllMerchantPolicies(
            empty_pb2.Empty(), timeout=5
        )
        assert restored_all.message == "Successfully restored all merchant policies"

        active = await query.FindByActive(
            merchant_query_pb2.FindAllMerchantRequest(
                page=1, page_size=10, search=name
            ),
            timeout=5,
        )
        assert any(r.id == policy_id for r in active.data)

        await command.TrashedMerchantPolicies(
            merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=policy_id),
            timeout=5,
        )
        deleted_all = await command.DeleteAllMerchantPoliciesPermanent(
            empty_pb2.Empty(), timeout=5
        )
        assert (
            deleted_all.message
            == "Successfully deleted all merchant policies permanently"
        )
    finally:
        await channel.close()
        await _cleanup(db, merchant_id, user_id)


__all__ = []
