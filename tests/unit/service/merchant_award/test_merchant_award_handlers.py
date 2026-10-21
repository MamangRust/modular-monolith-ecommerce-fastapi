"""Unit tests for the merchant_award gRPC handlers. Timestamps are emitted as `%Y-%m-%d %H:%M:%S.mmm`; `issue_date`/`expiry_date` are SQL `DATE` columns emitted as bare `%Y-%m-%d` (`pgtype.Date` branch). `merchant_name` is never projected to the wire."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.merchant import merchant_common_pb2, merchant_query_pb2
from pb.merchant_award import (
    merchant_award_command_pb2,
    merchant_award_common_pb2,
)
from pkg.database.schema.merchant_award import (
    CreateMerchantCertificationOrAwardRow,
    GetMerchantCertificationOrAwardRow,
    GetMerchantCertificationsAndAwardsActiveRow,
    GetMerchantCertificationsAndAwardsRow,
    MerchantCertificationsAndAward,
)
from pkg.logger.logger import Logger
from service.merchant_award.handler.merchant_award_command import (
    MerchantAwardCommandHandler,
)
from service.merchant_award.handler.merchant_award_query import (
    MerchantAwardQueryHandler,
)

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 1, 5, 6, 7)
ISSUED = date(2026, 1, 2)
EXPIRY = date(2027, 1, 2)


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


def _logger() -> Logger:
    return Logger("test", "error")


# ---- query handler ----


def _list_row(award_id: int = 1, total: int = 11) -> GetMerchantCertificationsAndAwardsRow:
    return GetMerchantCertificationsAndAwardsRow(
        merchant_certification_id=award_id,
        merchant_id=10,
        title="ISO 9001",
        description="Quality management",
        issued_by="BSN",
        issue_date=ISSUED,
        expiry_date=EXPIRY,
        certificate_url="https://certs.example.com/1",
        created_at=CREATED,
        updated_at=UPDATED,
        merchant_name="Elektronik Store",
        total_count=total,
    )


def _active_row(
    deleted_at: datetime | None = None,
) -> GetMerchantCertificationsAndAwardsActiveRow:
    return GetMerchantCertificationsAndAwardsActiveRow(
        merchant_certification_id=1,
        merchant_id=10,
        title="ISO 9001",
        description="Quality management",
        issued_by="BSN",
        issue_date=ISSUED,
        expiry_date=None,
        certificate_url=None,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        merchant_name="Elektronik Store",
        total_count=1,
    )


def _by_id_row() -> GetMerchantCertificationOrAwardRow:
    return GetMerchantCertificationOrAwardRow(
        merchant_certification_id=1,
        merchant_id=10,
        title="ISO 9001",
        description="Quality management",
        issued_by="BSN",
        issue_date=ISSUED,
        expiry_date=None,
        certificate_url=None,
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeQueryService:
    async def find_all(self, search, page, page_size):
        return [_list_row()], 11

    async def find_active(self, search, page, page_size):
        return [_active_row()], 1

    async def find_trashed(self, search, page, page_size):
        return [_active_row(deleted_at=DELETED)], 1

    async def find_by_id(self, merchant_certification_id):
        return _by_id_row()


def _query_handler() -> MerchantAwardQueryHandler:
    return MerchantAwardQueryHandler(FakeQueryService(), _logger())


async def test_query_find_all_formats_dates_and_timestamps() -> None:
    response = await _query_handler().FindAll(
        merchant_query_pb2.FindAllMerchantRequest(page=0, page_size=0),
        FakeContext(),
    )
    assert response.message == "Successfully fetched merchant"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_records == 11
    assert response.data[0].created_at == "2026-01-02 03:04:05.000"
    assert response.data[0].updated_at == "2026-01-03 04:05:06.000"
    # DATE columns use the date-only layout.
    assert response.data[0].issue_date == "2026-01-02"
    assert response.data[0].expiry_date == "2027-01-02"


async def test_query_find_all_never_fills_merchant_name() -> None:
    response = await _query_handler().FindAll(
        merchant_query_pb2.FindAllMerchantRequest(page=1, page_size=10),
        FakeContext(),
    )
    # mapping never reads the joined merchant_name column.
    assert response.data[0].merchant_name == ""


async def test_query_find_by_active_omits_deleted_at_wrapper_when_null() -> None:
    response = await _query_handler().FindByActive(
        merchant_query_pb2.FindAllMerchantRequest(page=1, page_size=10),
        FakeContext(),
    )
    assert response.message == "Successfully fetched active merchant"
    assert response.data[0].HasField("deleted_at") is False


async def test_query_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        merchant_query_pb2.FindAllMerchantRequest(page=1, page_size=10),
        FakeContext(),
    )
    assert response.message == "Successfully fetched trashed merchant"
    assert response.data[0].HasField("deleted_at") is True
    assert response.data[0].deleted_at.value == "2026-02-01 05:06:07.000"


async def test_query_find_by_id_success() -> None:
    response = await _query_handler().FindById(
        merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully fetched merchant"
    assert response.data.id == 1
    assert response.data.issue_date == "2026-01-02"
    # No expiry on this row -> empty string (a NULL value).
    assert response.data.expiry_date == ""


async def test_query_find_by_id_zero_is_internal_not_bad_request() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindById(
            merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=0), context
        )
    # returns errors.ToGrpcError(errors.ErrInternal) here
    # not a dedicated 400 invalid-id error.
    assert excinfo.value.code is grpc.StatusCode.INTERNAL
    assert excinfo.value.message == "Internal server error"
    assert context.metadata


# ---- command handler ----


class FakeCommandService:
    def __init__(self) -> None:
        self.last_update: Any = None

    async def create(self, request):
        return CreateMerchantCertificationOrAwardRow(
            merchant_certification_id=9,
            merchant_id=request.merchant_id,
            title=request.title,
            description=request.description,
            issued_by=request.issued_by,
            issue_date=ISSUED,
            expiry_date=EXPIRY,
            certificate_url=request.certificate_url or None,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.last_update = request
        return CreateMerchantCertificationOrAwardRow(
            merchant_certification_id=request.merchant_certification_id,
            merchant_id=10,
            title=request.title,
            description=request.description,
            issued_by=request.issued_by,
            issue_date=ISSUED,
            expiry_date=EXPIRY,
            certificate_url=request.certificate_url or None,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, merchant_certification_id):
        return MerchantCertificationsAndAward(
            merchant_certification_id=merchant_certification_id,
            merchant_id=10,
            title="ISO 9001",
            description="Quality management",
            issued_by="BSN",
            issue_date=ISSUED,
            expiry_date=EXPIRY,
            certificate_url=None,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, merchant_certification_id):
        return MerchantCertificationsAndAward(
            merchant_certification_id=merchant_certification_id,
            merchant_id=10,
            title="ISO 9001",
            description="Quality management",
            issued_by="BSN",
            issue_date=ISSUED,
            expiry_date=EXPIRY,
            certificate_url=None,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, merchant_certification_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all(self):
        return True


def _command_handler(service: FakeCommandService | None = None) -> MerchantAwardCommandHandler:
    return MerchantAwardCommandHandler(service or FakeCommandService(), _logger())


def _create_pb(**overrides: Any) -> Any:
    values = {
        "merchant_id": 10,
        "title": "ISO 9001",
        "description": "Quality management",
        "issued_by": "BSN",
        "issue_date": "2026-01-02",
        "expiry_date": "2027-01-02",
        "certificate_url": "https://certs.example.com/1",
    }
    values.update(overrides)
    return merchant_award_command_pb2.CreateMerchantAwardRequest(**values)


def _update_pb(**overrides: Any) -> Any:
    values = {
        "merchant_certification_id": 4,
        "title": "ISO 9001",
        "description": "Quality management",
        "issued_by": "BSN",
        "issue_date": "2026-01-02",
        "expiry_date": "2027-01-02",
        "certificate_url": "https://certs.example.com/1",
    }
    values.update(overrides)
    return merchant_award_command_pb2.UpdateMerchantAwardRequest(**values)


async def test_command_create_success() -> None:
    response = await _command_handler().Create(_create_pb(), FakeContext())
    assert response.message == "Successfully created merchant award"
    assert response.data.id == 9
    assert response.data.created_at == "2026-01-02 03:04:05.000"
    assert response.data.issue_date == "2026-01-02"


async def test_command_create_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(_create_pb(title=""), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid create merchant award request"
    )


async def test_command_create_rejects_bad_date() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(_create_pb(issue_date="2026/01/02"), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid create merchant award request"
    )


async def test_command_update_has_no_zero_id_guard() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).Update(
        _update_pb(merchant_certification_id=0), FakeContext()
    )
    # handler forwards the request (the repository then answers 404).
    assert service.last_update is not None
    assert service.last_update.merchant_certification_id == 0
    assert response.message == "Successfully updated merchant award"


async def test_command_update_success() -> None:
    response = await _command_handler().Update(_update_pb(), FakeContext())
    assert response.message == "Successfully updated merchant award"
    assert response.data.id == 4


async def test_command_update_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(_update_pb(title=""), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid update merchant award request"
    )


@pytest.mark.parametrize(
    "method_name",
    ["TrashedMerchantAward", "RestoreMerchantAward", "DeleteMerchantAwardPermanent"],
)
async def test_command_id_guards_reject_zero(method_name: str) -> None:
    context = FakeContext()
    handler = _command_handler()
    with pytest.raises(FakeAbort) as excinfo:
        await getattr(handler, method_name)(
            merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "Invalid merchant ID"


async def test_command_trash_restore_return_delete_at_shape() -> None:
    trashed = await _command_handler().TrashedMerchantAward(
        merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=1), FakeContext()
    )
    restored = await _command_handler().RestoreMerchantAward(
        merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=1), FakeContext()
    )
    assert trashed.message == "Successfully trashed merchant award"
    assert trashed.data.deleted_at.value == "2026-02-01 05:06:07.000"
    assert restored.message == "Successfully restored merchant award"
    assert restored.data.HasField("deleted_at") is False


async def test_command_bulk_and_permanent_use_merchant_envelopes() -> None:
    handler = _command_handler()
    deleted = await handler.DeleteMerchantAwardPermanent(
        merchant_award_common_pb2.FindByIdMerchantAwardRequest(id=1), FakeContext()
    )
    restored_all = await handler.RestoreAllMerchantAward(
        empty_pb2.Empty(), FakeContext()
    )
    deleted_all = await handler.DeleteAllMerchantAwardPermanent(
        empty_pb2.Empty(), FakeContext()
    )
    assert isinstance(deleted, merchant_common_pb2.ApiResponseMerchantDelete)
    assert isinstance(restored_all, merchant_common_pb2.ApiResponseMerchantAll)
    assert isinstance(deleted_all, merchant_common_pb2.ApiResponseMerchantAll)
    assert deleted.message == "Successfully deleted merchant award permanently"
    assert restored_all.message == "Successfully restored all trashed merchant awards"
    assert (
        deleted_all.message == "Successfully deleted all merchant awards permanently"
    )


__all__ = []
