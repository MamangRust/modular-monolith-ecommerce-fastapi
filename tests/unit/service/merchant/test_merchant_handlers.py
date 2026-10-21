"""Unit tests for merchant + merchant_document gRPC handlers (no server/DB). Merchant timestamps are emitted as `%Y-%m-%d %H:%M:%S` . `FindById` guards `id == 0` with a 400 `invalid merchant ID`; every id-carrying command guards `id == 0` with the same error. The document handlers guard `document_id == 0` with 400 `invalid ID provided`. Validation failures raise the sentinels verbatim (`Create`/`Update` for merchant; `Create` 400 / `Update` 500 for documents)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.merchant import merchant_command_pb2, merchant_common_pb2, merchant_query_pb2
from pb.merchant_document import (
    merchant_document_command_pb2,
    merchant_document_query_pb2,
)
from pkg.database.schema.merchant import (
    CreateMerchantRow,
    GetMerchantsActiveRow,
    GetMerchantsRow,
    Merchant,
)
from pkg.database.schema.merchant_document import (
    CreateMerchantDocumentRow,
    GetActiveMerchantDocumentsRow,
    GetMerchantDocumentsRow,
    MerchantDocument,
)
from pkg.logger.logger import Logger
from service.merchant.handler.merchant_command import MerchantCommandHandler
from service.merchant.handler.merchant_document_command import (
    MerchantDocumentCommandHandler,
)
from service.merchant.handler.merchant_document_query import (
    MerchantDocumentQueryHandler,
)
from service.merchant.handler.merchant_query import MerchantQueryHandler

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 1, 5, 6, 7)


class FakeAbort(Exception):
    def __init__(self, code: grpc.StatusCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class FakeContext:
    def __init__(self) -> None:
        self.metadata: tuple[Any, ...] = ()
        self.aborted: FakeAbort | None = None

    def set_trailing_metadata(self, metadata: tuple[Any, ...]) -> None:
        self.metadata = metadata

    async def abort(self, code: grpc.StatusCode, message: str) -> None:
        self.aborted = FakeAbort(code, message)
        raise self.aborted


def _merchant_row(merchant_id: int = 1, total: int = 11) -> GetMerchantsRow:
    return GetMerchantsRow(
        merchant_id=merchant_id,
        user_id=10,
        name="Elektronik Store",
        description="d",
        address="a",
        contact_email="e@f.com",
        contact_phone="0812",
        status="active",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _merchant_active_row(deleted_at: datetime | None = None) -> GetMerchantsActiveRow:
    return GetMerchantsActiveRow(
        merchant_id=1,
        user_id=10,
        name="N",
        description=None,
        address=None,
        contact_email=None,
        contact_phone=None,
        status="active",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=1,
    )


def _merchant_by_id() -> CreateMerchantRow:
    return CreateMerchantRow(
        merchant_id=1,
        user_id=10,
        name="N",
        description=None,
        address=None,
        contact_email=None,
        contact_phone=None,
        status="active",
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeQueryService:
    async def find_all(self, search, page, page_size):
        return [_merchant_row()], 11

    async def find_active(self, search, page, page_size):
        return [_merchant_active_row()], 1

    async def find_trashed(self, search, page, page_size):
        return [_merchant_active_row(deleted_at=DELETED)], 1

    async def find_by_id(self, merchant_id):
        return _merchant_by_id()


class FakeCommandService:
    async def create(self, request):
        return CreateMerchantRow(
            merchant_id=1,
            user_id=request.user_id,
            name=request.name,
            description=request.description,
            address=request.address,
            contact_email=request.contact_email,
            contact_phone=request.contact_phone,
            status=request.status,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        return CreateMerchantRow(
            merchant_id=request.merchant_id or 1,
            user_id=request.user_id,
            name=request.name,
            description=request.description,
            address=request.address,
            contact_email=request.contact_email,
            contact_phone=request.contact_phone,
            status=request.status,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update_status(self, request):
        return CreateMerchantRow(
            merchant_id=request.merchant_id or 1,
            user_id=10,
            name="N",
            description=None,
            address=None,
            contact_email=None,
            contact_phone=None,
            status=request.status,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, merchant_id):
        return Merchant(
            merchant_id=merchant_id,
            user_id=10,
            name="N",
            description=None,
            address=None,
            contact_email=None,
            contact_phone=None,
            status="active",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, merchant_id):
        return Merchant(
            merchant_id=merchant_id,
            user_id=10,
            name="N",
            description=None,
            address=None,
            contact_email=None,
            contact_phone=None,
            status="active",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, merchant_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all(self):
        return True


def _logger() -> Logger:
    return Logger("test", "error")


def _query_handler() -> MerchantQueryHandler:
    return MerchantQueryHandler(FakeQueryService(), _logger())


def _command_handler() -> MerchantCommandHandler:
    return MerchantCommandHandler(FakeCommandService(), _logger())


async def test_merchant_find_all_timestamp_format() -> None:
    response = await _query_handler().FindAll(
        merchant_query_pb2.FindAllMerchantRequest(page=0, page_size=0), FakeContext()
    )
    assert response.message == "Successfully fetched merchants"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_records == 11
    assert response.data[0].created_at == "2026-01-02 03:04:05"
    assert response.data[0].updated_at == "2026-01-03 04:05:06"


async def test_merchant_find_by_active_omits_deleted_at_wrapper_when_null() -> None:
    response = await _query_handler().FindByActive(
        merchant_query_pb2.FindAllMerchantRequest(page=1, page_size=10), FakeContext()
    )
    assert response.message == "Successfully fetched active merchants"
    assert response.data[0].HasField("deleted_at") is False


async def test_merchant_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        merchant_query_pb2.FindAllMerchantRequest(page=1, page_size=10), FakeContext()
    )
    assert response.message == "Successfully fetched trashed merchants"
    assert response.data[0].HasField("deleted_at") is True
    assert response.data[0].deleted_at.value == "2026-02-01 05:06:07"


async def test_merchant_find_by_id_success() -> None:
    response = await _query_handler().FindById(
        merchant_common_pb2.FindByIdMerchantRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully fetched merchant"
    assert response.data.id == 1


async def test_merchant_find_by_id_rejects_zero() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindById(
            merchant_common_pb2.FindByIdMerchantRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid merchant ID"
    assert context.metadata


async def test_merchant_create_success() -> None:
    response = await _command_handler().Create(
        merchant_command_pb2.CreateMerchantRequest(
            user_id=10,
            name="N",
            description="d",
            address="a",
            contact_email="e@f.com",
            contact_phone="0812",
            status="active",
        ),
        FakeContext(),
    )
    assert response.message == "Successfully created merchant"
    assert response.data.id == 1


async def test_merchant_create_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(
            merchant_command_pb2.CreateMerchantRequest(
                user_id=10,
                name="",  # invalid: required
                description="d",
                address="a",
                contact_email="e@f.com",
                contact_phone="0812",
                status="active",
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "Validation failed: invalid create merchant request"


async def test_merchant_update_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(
            merchant_command_pb2.UpdateMerchantRequest(
                merchant_id=0,
                user_id=10,
                name="N",
                description="d",
                address="a",
                contact_email="e@f.com",
                contact_phone="0812",
                status="active",
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid merchant ID"


async def test_merchant_update_success() -> None:
    response = await _command_handler().Update(
        merchant_command_pb2.UpdateMerchantRequest(
            merchant_id=1,
            user_id=10,
            name="N",
            description="d",
            address="a",
            contact_email="e@f.com",
            contact_phone="0812",
            status="active",
        ),
        FakeContext(),
    )
    assert response.message == "Successfully updated merchant"
    assert response.data.id == 1


async def test_merchant_update_status_uses_update_sentinel_on_validation_error() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().UpdateStatus(
            merchant_command_pb2.UpdateMerchantStatusRequest(merchant_id=1, status=""),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "Validation failed: invalid update merchant request"


async def test_merchant_trashed_returns_delete_at_shape() -> None:
    response = await _command_handler().TrashedMerchant(
        merchant_common_pb2.FindByIdMerchantRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully trashed merchant"
    assert response.data.deleted_at.value == "2026-02-01 05:06:07"


async def test_merchant_restore_success() -> None:
    response = await _command_handler().RestoreMerchant(
        merchant_common_pb2.FindByIdMerchantRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully restored merchant"


async def test_merchant_delete_permanent_success() -> None:
    response = await _command_handler().DeleteMerchantPermanent(
        merchant_common_pb2.FindByIdMerchantRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully deleted merchant permanently"


async def test_merchant_restore_all_and_delete_all() -> None:
    restored = await _command_handler().RestoreAllMerchant(
        empty_pb2.Empty(), FakeContext()
    )
    deleted = await _command_handler().DeleteAllMerchantPermanent(
        empty_pb2.Empty(), FakeContext()
    )
    assert restored.message == "Successfully restored all merchants"
    assert deleted.message == "Successfully deleted all merchants permanently"


# ---- documents ----


def _document_row(document_id: int = 1, total: int = 3) -> GetMerchantDocumentsRow:
    return GetMerchantDocumentsRow(
        document_id=document_id,
        merchant_id=10,
        document_type="NIB",
        document_url="uploads/merchant_document/a.pdf",
        status="pending",
        note=None,
        uploaded_at=CREATED,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _document_active_row(
    deleted_at: datetime | None = None,
) -> GetActiveMerchantDocumentsRow:
    return GetActiveMerchantDocumentsRow(
        document_id=1,
        merchant_id=10,
        document_type="NIB",
        document_url="u",
        status="approved",
        note="ok",
        uploaded_at=CREATED,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=1,
    )


def _document_by_id() -> CreateMerchantDocumentRow:
    return CreateMerchantDocumentRow(
        document_id=1,
        merchant_id=10,
        document_type="NIB",
        document_url="u",
        status="pending",
        note=None,
        uploaded_at=CREATED,
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeDocumentQueryService:
    async def find_all(self, search, page, page_size):
        return [_document_row()], 3

    async def find_active(self, search, page, page_size):
        return [_document_active_row()], 1

    async def find_trashed(self, search, page, page_size):
        return [_document_active_row(deleted_at=DELETED)], 1

    async def find_by_id(self, document_id):
        return _document_by_id()


class FakeDocumentCommandService:
    async def create(self, request):
        return CreateMerchantDocumentRow(
            document_id=1,
            merchant_id=request.merchant_id,
            document_type=request.document_type,
            document_url=request.document_url,
            status="pending",
            note=None,
            uploaded_at=CREATED,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        return CreateMerchantDocumentRow(
            document_id=request.document_id or 1,
            merchant_id=request.merchant_id,
            document_type=request.document_type,
            document_url=request.document_url,
            status=request.status,
            note=request.note,
            uploaded_at=CREATED,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update_status(self, request):
        return CreateMerchantDocumentRow(
            document_id=request.document_id or 1,
            merchant_id=request.merchant_id,
            document_type="NIB",
            document_url="u",
            status=request.status,
            note=request.note,
            uploaded_at=CREATED,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, document_id):
        return MerchantDocument(
            document_id=document_id,
            merchant_id=10,
            document_type="NIB",
            document_url="u",
            status="pending",
            note=None,
            uploaded_at=CREATED,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, document_id):
        return MerchantDocument(
            document_id=document_id,
            merchant_id=10,
            document_type="NIB",
            document_url="u",
            status="pending",
            note=None,
            uploaded_at=CREATED,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, document_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all(self):
        return True


def _document_query_handler() -> MerchantDocumentQueryHandler:
    return MerchantDocumentQueryHandler(FakeDocumentQueryService(), _logger())


def _document_command_handler() -> MerchantDocumentCommandHandler:
    return MerchantDocumentCommandHandler(FakeDocumentCommandService(), _logger())


async def test_document_find_all() -> None:
    response = await _document_query_handler().FindAll(
        merchant_document_query_pb2.FindAllMerchantDocumentsRequest(
            page=1, page_size=10
        ),
        FakeContext(),
    )
    assert response.message == "Successfully fetched merchant documents"
    assert response.data[0].document_id == 1
    # proto uploaded_at is filled from the row created_at by the handler mapping.
    assert response.data[0].uploaded_at == "2026-01-02 03:04:05"


async def test_document_find_active_and_trashed() -> None:
    active = await _document_query_handler().FindAllActive(
        merchant_document_query_pb2.FindAllMerchantDocumentsRequest(
            page=1, page_size=10
        ),
        FakeContext(),
    )
    trashed = await _document_query_handler().FindAllTrashed(
        merchant_document_query_pb2.FindAllMerchantDocumentsRequest(
            page=1, page_size=10
        ),
        FakeContext(),
    )
    assert active.message == "Successfully fetched active merchant documents"
    assert trashed.message == "Successfully fetched trashed merchant documents"
    assert trashed.data[0].deleted_at.value == "2026-02-01 05:06:07"


async def test_document_find_by_id_guards_zero() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _document_query_handler().FindById(
            merchant_document_query_pb2.FindMerchantDocumentByIdRequest(document_id=0),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID provided"


async def test_document_create_success() -> None:
    response = await _document_command_handler().Create(
        merchant_document_command_pb2.CreateMerchantDocumentRequest(
            merchant_id=10, document_type="NIB", document_url="u"
        ),
        FakeContext(),
    )
    assert response.message == "Successfully created merchant document"
    assert response.data.document_id == 1


async def test_document_create_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _document_command_handler().Create(
            merchant_document_command_pb2.CreateMerchantDocumentRequest(
                merchant_id=0, document_type="NIB", document_url="u"
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid create merchant document request"
    )


async def test_document_update_validation_failure_is_500() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _document_command_handler().Update(
            merchant_document_command_pb2.UpdateMerchantDocumentRequest(
                document_id=1,
                merchant_id=10,
                document_type="NIB",
                document_url="u",
                status="pending",
                note="",  # invalid: required
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INTERNAL
    assert excinfo.value.message == "Failed to update merchant document"


async def test_document_update_status_guards_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _document_command_handler().UpdateStatus(
            merchant_document_command_pb2.UpdateMerchantDocumentStatusRequest(
                document_id=0, merchant_id=10, status="approved", note="ok"
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid ID provided"


async def test_document_trash_restore_delete_and_bulk() -> None:
    trashed = await _document_command_handler().Trashed(
        merchant_document_command_pb2.TrashedMerchantDocumentRequest(document_id=1),
        FakeContext(),
    )
    restored = await _document_command_handler().Restore(
        merchant_document_command_pb2.RestoreMerchantDocumentRequest(document_id=1),
        FakeContext(),
    )
    deleted = await _document_command_handler().DeletePermanent(
        merchant_document_command_pb2.DeleteMerchantDocumentPermanentRequest(
            document_id=1
        ),
        FakeContext(),
    )
    restored_all = await _document_command_handler().RestoreAll(
        empty_pb2.Empty(), FakeContext()
    )
    deleted_all = await _document_command_handler().DeleteAllPermanent(
        empty_pb2.Empty(), FakeContext()
    )
    assert trashed.message == "Successfully trashed merchant document"
    assert restored.message == "Successfully restored merchant document"
    assert deleted.message == "Successfully permanently deleted merchant document"
    assert restored_all.message == "Successfully restored all merchant documents"
    assert (
        deleted_all.message
        == "Successfully permanently deleted all merchant documents"
    )


__all__ = []
