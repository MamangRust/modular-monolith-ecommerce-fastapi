"""Merchant document repository integration tests against a real PostgreSQL.

Marked `integration`. `merchant_documents.merchant_id` has an
`ON DELETE CASCADE` FK to `merchants`, so each test seeds its own user +
merchant and removes them afterwards (which cascades the documents).

: document `Create` hardcodes `status = 'pending'` and a NULL note;
`FindAll`/`FindActive` filter `deleted_at IS NULL`, `FindTrashed` filters
`IS NOT NULL`, `FindById` adds `AND deleted_at IS NULL`. Unlike the merchant
repository, the document delete paths have no FK-conflict branch."""

from __future__ import annotations

import uuid

import grpc
import pytest

from service.merchant.repository import GuardOptions, new_repositories
from shared.domain.requests.merchant import (
    CreateMerchantDocumentRequest,
    UpdateMerchantDocumentRequest,
    UpdateMerchantDocumentStatusRequest,
)
from shared.errors import AppError

pytestmark = pytest.mark.integration


@pytest.fixture
async def repos(db):
    channel = grpc.aio.insecure_channel("127.0.0.1:1")
    try:
        yield new_repositories(db, user_channel=channel, guards=GuardOptions())
    finally:
        await channel.close()


def _doc_type() -> str:
    return f"TYPE{uuid.uuid4().hex[:6]}"


async def _seed_merchant(db) -> tuple[int, int]:
    email = f"test_merchant_doc_{uuid.uuid4().hex[:10]}@example.com"
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
        INSERT INTO merchants (user_id, name, status)
        VALUES (:user_id, :name, 'active')
        RETURNING merchant_id
        """,
        {"user_id": user_id, "name": f"Merchant {uuid.uuid4().hex[:10]}"},
    )
    assert merchant is not None
    return user_id, int(merchant["merchant_id"])


async def _cleanup(db, user_id: int, merchant_id: int) -> None:
    await db.execute(
        "DELETE FROM merchant_documents WHERE merchant_id = :merchant_id",
        {"merchant_id": merchant_id},
    )
    await db.execute(
        "DELETE FROM merchants WHERE merchant_id = :merchant_id",
        {"merchant_id": merchant_id},
    )
    await db.execute("DELETE FROM users WHERE user_id = :user_id", {"user_id": user_id})


def _create(merchant_id: int, document_type: str) -> CreateMerchantDocumentRequest:
    return CreateMerchantDocumentRequest(
        merchant_id=merchant_id,
        document_type=document_type,
        document_url="uploads/merchant_document/a.pdf",
    )


async def test_create_and_find(db, repos) -> None:
    user_id, merchant_id = await _seed_merchant(db)
    document_type = _doc_type()
    try:
        created = await repos.merchant_document_command.create(
            _create(merchant_id, document_type)
        )
        assert created.document_id > 0
        assert created.status == "pending"
        assert created.note is None

        by_id = await repos.merchant_document_query.find_by_id(created.document_id)
        assert by_id.document_id == created.document_id

        rows, total = await repos.merchant_document_query.find_all(document_type, 1, 10)
        assert total >= 1
        assert any(row.document_id == created.document_id for row in rows)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_update_and_update_status(db, repos) -> None:
    user_id, merchant_id = await _seed_merchant(db)
    document_type = _doc_type()
    try:
        created = await repos.merchant_document_command.create(
            _create(merchant_id, document_type)
        )
        updated = await repos.merchant_document_command.update(
            UpdateMerchantDocumentRequest(
                document_id=created.document_id,
                merchant_id=merchant_id,
                document_type=f"{document_type}X",
                document_url="uploads/merchant_document/b.pdf",
                status="pending",
                note="reviewed",
            )
        )
        assert updated.document_type == f"{document_type}X"
        assert updated.note == "reviewed"

        status_row = await repos.merchant_document_command.update_status(
            UpdateMerchantDocumentStatusRequest(
                document_id=created.document_id,
                merchant_id=merchant_id,
                status="approved",
                note="ok",
            )
        )
        assert status_row.status == "approved"
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_soft_delete_lifecycle(db, repos) -> None:
    user_id, merchant_id = await _seed_merchant(db)
    document_type = _doc_type()
    try:
        created = await repos.merchant_document_command.create(
            _create(merchant_id, document_type)
        )

        trashed = await repos.merchant_document_command.trash(created.document_id)
        assert trashed.deleted_at is not None

        active_rows, _ = await repos.merchant_document_query.find_active(
            document_type, 1, 10
        )
        assert all(row.document_id != created.document_id for row in active_rows)
        trashed_rows, _ = await repos.merchant_document_query.find_trashed(
            document_type, 1, 10
        )
        assert any(row.document_id == created.document_id for row in trashed_rows)

        with pytest.raises(AppError) as missing:
            await repos.merchant_document_query.find_by_id(created.document_id)
        assert missing.value.code == 404

        restored = await repos.merchant_document_command.restore(created.document_id)
        assert restored.deleted_at is None
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_delete_permanent_requires_trashed(db, repos) -> None:
    user_id, merchant_id = await _seed_merchant(db)
    document_type = _doc_type()
    try:
        created = await repos.merchant_document_command.create(
            _create(merchant_id, document_type)
        )

        # A live row is not deleted.
        await repos.merchant_document_command.delete_permanent(created.document_id)
        still_there = await repos.merchant_document_query.find_by_id(created.document_id)
        assert still_there.document_id == created.document_id

        await repos.merchant_document_command.trash(created.document_id)
        await repos.merchant_document_command.delete_permanent(created.document_id)
        trashed_rows, _ = await repos.merchant_document_query.find_trashed(
            document_type, 1, 10
        )
        assert all(row.document_id != created.document_id for row in trashed_rows)
    finally:
        await _cleanup(db, user_id, merchant_id)


async def test_missing_document_maps_to_not_found(db, repos) -> None:
    with pytest.raises(AppError) as excinfo:
        await repos.merchant_document_query.find_by_id(2_000_000_000)
    assert excinfo.value.code == 404

    with pytest.raises(AppError) as trash_missing:
        await repos.merchant_document_command.trash(2_000_000_000)
    assert trash_missing.value.code == 404


async def test_pagination_reports_total_count(db, repos) -> None:
    user_id, merchant_id = await _seed_merchant(db)
    document_type = _doc_type()
    try:
        for _ in range(3):
            await repos.merchant_document_command.create(
                _create(merchant_id, document_type)
            )
        rows, total = await repos.merchant_document_query.find_all(document_type, 1, 2)
        assert len(rows) == 2
        assert total >= 3
    finally:
        await _cleanup(db, user_id, merchant_id)


__all__ = []
