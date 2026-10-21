"""Merchant gRPC integration tests: real grpc.aio server, generated client. Marked `integration`. Runs the four real merchant servicers (merchant query/ command + document query/command) behind an ephemeral port, with the user adapter pointed at the real user server. Verifies the wire contract (the `%Y-%m-%d %H:%M:%S` timestamps, the `deleted_at` wrapper only on the `...DeleteAt` projections, the `uploaded_at` field) and the error mapping (400 guards survive as INVALID_ARGUMENT, a repository 404 stays NOT_FOUND)."""

from __future__ import annotations

import uuid

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.merchant import (
    merchant_command_pb2,
    merchant_command_pb2_grpc,
    merchant_common_pb2,
    merchant_query_pb2,
    merchant_query_pb2_grpc,
)
from pb.merchant_document import (
    merchant_document_command_pb2,
    merchant_document_command_pb2_grpc,
    merchant_document_query_pb2,
    merchant_document_query_pb2_grpc,
)
from pkg.database.database import Database
from shared.errors import parse_grpc_error

pytestmark = pytest.mark.integration


async def _seed_user(db: Database) -> int:
    email = f"test_merchant_grpc_{uuid.uuid4().hex[:10]}@example.com"
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
            "DELETE FROM merchant_documents WHERE merchant_id = :merchant_id",
            {"merchant_id": merchant_id},
        )
        await db.execute(
            "DELETE FROM merchants WHERE merchant_id = :merchant_id",
            {"merchant_id": merchant_id},
        )
    await db.execute("DELETE FROM outbox_events WHERE event_key LIKE 'merchant-%'")
    await db.execute("DELETE FROM users WHERE user_id = :user_id", {"user_id": user_id})


async def test_merchant_grpc_lifecycle(db: Database, merchant_grpc_server: str) -> None:
    channel = grpc.aio.insecure_channel(merchant_grpc_server)
    query = merchant_query_pb2_grpc.MerchantQueryServiceStub(channel)
    command = merchant_command_pb2_grpc.MerchantCommandServiceStub(channel)
    user_id = await _seed_user(db)
    name = f"Merchant {uuid.uuid4().hex[:10]}"
    merchant_id: int | None = None

    try:
        created = await command.Create(
            merchant_command_pb2.CreateMerchantRequest(
                user_id=user_id,
                name=name,
                description="d",
                address="a",
                contact_email="e@f.com",
                contact_phone="0812",
                status="inactive",  # ignored on create
            ),
            timeout=5,
        )
        assert created.status == "success"
        assert created.message == "Successfully created merchant"
        assert created.data.name == name
        assert created.data.status == "active"
        assert created.data.created_at
        # `%Y-%m-%d %H:%M:%S` (19 chars), not date-only.
        assert len(created.data.created_at) == 19
        merchant_id = created.data.id

        found = await query.FindById(
            merchant_common_pb2.FindByIdMerchantRequest(id=merchant_id), timeout=5
        )
        assert found.message == "Successfully fetched merchant"
        assert found.data.id == merchant_id

        listed = await query.FindAll(
            merchant_query_pb2.FindAllMerchantRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert listed.pagination.total_records >= 1

        trashed = await command.TrashedMerchant(
            merchant_common_pb2.FindByIdMerchantRequest(id=merchant_id), timeout=5
        )
        assert trashed.message == "Successfully trashed merchant"
        assert trashed.data.deleted_at.value

        trashed_rows = await query.FindByTrashed(
            merchant_query_pb2.FindAllMerchantRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert any(
            row.id == merchant_id and row.deleted_at.value for row in trashed_rows.data
        )

        restored = await command.RestoreMerchant(
            merchant_common_pb2.FindByIdMerchantRequest(id=merchant_id), timeout=5
        )
        assert restored.message == "Successfully restored merchant"

        updated = await command.Update(
            merchant_command_pb2.UpdateMerchantRequest(
                merchant_id=merchant_id,
                user_id=user_id,
                name=f"{name} v2",
                description="d2",
                address="a2",
                contact_email="e2@f.com",
                contact_phone="0899",
                status="active",
            ),
            timeout=5,
        )
        assert updated.message == "Successfully updated merchant"
        assert updated.data.name == f"{name} v2"

        # FindById guards id == 0 -> 400 invalid merchant ID.
        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await query.FindById(
                merchant_common_pb2.FindByIdMerchantRequest(id=0), timeout=5
            )
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        parsed = parse_grpc_error(invalid.value)
        assert parsed.code == 400
        assert parsed.message == "invalid merchant ID"

        # A repository 404 is preserved as NOT_FOUND.
        with pytest.raises(grpc.aio.AioRpcError) as missing:
            await command.TrashedMerchant(
                merchant_common_pb2.FindByIdMerchantRequest(id=2_000_000_000), timeout=5
            )
        assert missing.value.code() is grpc.StatusCode.NOT_FOUND
        assert parse_grpc_error(missing.value).code == 404

        await command.TrashedMerchant(
            merchant_common_pb2.FindByIdMerchantRequest(id=merchant_id), timeout=5
        )
        deleted = await command.DeleteMerchantPermanent(
            merchant_common_pb2.FindByIdMerchantRequest(id=merchant_id), timeout=5
        )
        assert deleted.message == "Successfully deleted merchant permanently"
        merchant_id = None
    finally:
        await channel.close()
        await _cleanup(db, merchant_id, user_id)


async def test_merchant_bulk_over_grpc(db: Database, merchant_grpc_server: str) -> None:
    channel = grpc.aio.insecure_channel(merchant_grpc_server)
    query = merchant_query_pb2_grpc.MerchantQueryServiceStub(channel)
    command = merchant_command_pb2_grpc.MerchantCommandServiceStub(channel)
    user_id = await _seed_user(db)
    name = f"Merchant {uuid.uuid4().hex[:10]}"
    merchant_id: int | None = None
    try:
        created = await command.Create(
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
        merchant_id = created.data.id
        await command.TrashedMerchant(
            merchant_common_pb2.FindByIdMerchantRequest(id=merchant_id), timeout=5
        )

        restored_all = await command.RestoreAllMerchant(empty_pb2.Empty(), timeout=5)
        assert restored_all.message == "Successfully restored all merchants"

        active = await query.FindByActive(
            merchant_query_pb2.FindAllMerchantRequest(page=1, page_size=10, search=name),
            timeout=5,
        )
        assert any(row.id == merchant_id for row in active.data)

        await command.TrashedMerchant(
            merchant_common_pb2.FindByIdMerchantRequest(id=merchant_id), timeout=5
        )
        deleted_all = await command.DeleteAllMerchantPermanent(
            empty_pb2.Empty(), timeout=5
        )
        assert deleted_all.message == "Successfully deleted all merchants permanently"
        merchant_id = None
    finally:
        await channel.close()
        await _cleanup(db, merchant_id, user_id)


async def test_merchant_document_grpc_lifecycle(
    db: Database, merchant_grpc_server: str
) -> None:
    channel = grpc.aio.insecure_channel(merchant_grpc_server)
    merchant_command = merchant_command_pb2_grpc.MerchantCommandServiceStub(channel)
    doc_command = (
        merchant_document_command_pb2_grpc.MerchantDocumentCommandServiceStub(channel)
    )
    doc_query = merchant_document_query_pb2_grpc.MerchantDocumentQueryServiceStub(
        channel
    )
    user_id = await _seed_user(db)
    name = f"Merchant {uuid.uuid4().hex[:10]}"
    document_type = f"TYPE{uuid.uuid4().hex[:6]}"
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

        created = await doc_command.Create(
            merchant_document_command_pb2.CreateMerchantDocumentRequest(
                merchant_id=merchant_id,
                document_type=document_type,
                document_url="uploads/merchant_document/a.pdf",
            ),
            timeout=5,
        )
        assert created.message == "Successfully created merchant document"
        assert created.data.status == "pending"
        assert created.data.uploaded_at  # filled from created_at
        document_id = created.data.document_id

        listed = await doc_query.FindAll(
            merchant_document_query_pb2.FindAllMerchantDocumentsRequest(
                page=1, page_size=10, search=document_type
            ),
            timeout=5,
        )
        assert listed.pagination.total_records >= 1

        found = await doc_query.FindById(
            merchant_document_query_pb2.FindMerchantDocumentByIdRequest(
                document_id=document_id
            ),
            timeout=5,
        )
        assert found.data.document_id == document_id

        status_row = await doc_command.UpdateStatus(
            merchant_document_command_pb2.UpdateMerchantDocumentStatusRequest(
                document_id=document_id,
                merchant_id=merchant_id,
                status="approved",
                note="ok",
            ),
            timeout=5,
        )
        assert status_row.message == "Successfully updated merchant document status"
        assert status_row.data.status == "approved"

        trashed = await doc_command.Trashed(
            merchant_document_command_pb2.TrashedMerchantDocumentRequest(
                document_id=document_id
            ),
            timeout=5,
        )
        # maps Trashed to MerchantDocument (no deleted_at field) — assert the
        # message/id, not deleted_at.
        assert trashed.message == "Successfully trashed merchant document"
        assert trashed.data.document_id == document_id

        restored = await doc_command.Restore(
            merchant_document_command_pb2.RestoreMerchantDocumentRequest(
                document_id=document_id
            ),
            timeout=5,
        )
        assert restored.message == "Successfully restored merchant document"

        # Document FindById guards document_id == 0 -> 400 invalid ID provided.
        with pytest.raises(grpc.aio.AioRpcError) as invalid:
            await doc_query.FindById(
                merchant_document_query_pb2.FindMerchantDocumentByIdRequest(
                    document_id=0
                ),
                timeout=5,
            )
        assert invalid.value.code() is grpc.StatusCode.INVALID_ARGUMENT
        parsed = parse_grpc_error(invalid.value)
        assert parsed.code == 400
        assert parsed.message == "invalid ID provided"

        await doc_command.Trashed(
            merchant_document_command_pb2.TrashedMerchantDocumentRequest(
                document_id=document_id
            ),
            timeout=5,
        )
        deleted = await doc_command.DeletePermanent(
            merchant_document_command_pb2.DeleteMerchantDocumentPermanentRequest(
                document_id=document_id
            ),
            timeout=5,
        )
        assert deleted.message == "Successfully permanently deleted merchant document"
    finally:
        await channel.close()
        await _cleanup(db, merchant_id, user_id)


__all__ = []
