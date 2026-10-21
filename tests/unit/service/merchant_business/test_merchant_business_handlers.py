"""Unit tests for the merchant_business gRPC handlers. All timestamps are emitted as `%Y-%m-%d %H:%M:%S.mmm` (the table has no DATE columns, unlike merchant_award). `merchant_name` is never projected to the wire."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.merchant import merchant_common_pb2, merchant_query_pb2
from pb.merchant_business import (
    merchant_business_command_pb2,
    merchant_business_common_pb2,
)
from pkg.database.schema.merchant_business import (
    CreateMerchantBusinessInformationRow,
    GetMerchantBusinessInformationRow,
    GetMerchantsBusinessInformationActiveRow,
    GetMerchantsBusinessInformationRow,
    MerchantBusinessInformation,
)
from pkg.logger.logger import Logger
from service.merchant_business.handler.merchant_business_command import (
    MerchantBusinessCommandHandler,
)
from service.merchant_business.handler.merchant_business_query import (
    MerchantBusinessQueryHandler,
)

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


def _logger() -> Logger:
    return Logger("test", "error")


# ---- query handler ----


def _list_row(
    business_id: int = 1, total: int = 11
) -> GetMerchantsBusinessInformationRow:
    return GetMerchantsBusinessInformationRow(
        merchant_business_info_id=business_id,
        merchant_id=10,
        business_type="Toko Elektronik",
        tax_id="01.234.567.8-999.000",
        established_year=2010,
        number_of_employees=15,
        website_url="https://technostore.com",
        created_at=CREATED,
        updated_at=UPDATED,
        merchant_name="Elektronik Store",
        total_count=total,
    )


def _active_row(
    deleted_at: datetime | None = None,
) -> GetMerchantsBusinessInformationActiveRow:
    return GetMerchantsBusinessInformationActiveRow(
        merchant_business_info_id=1,
        merchant_id=10,
        business_type="Toko Elektronik",
        tax_id=None,
        established_year=None,
        number_of_employees=None,
        website_url=None,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        merchant_name="Elektronik Store",
        total_count=1,
    )


def _by_id_row() -> GetMerchantBusinessInformationRow:
    return GetMerchantBusinessInformationRow(
        merchant_business_info_id=1,
        merchant_id=10,
        business_type="Toko Elektronik",
        tax_id=None,
        established_year=None,
        number_of_employees=None,
        website_url=None,
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

    async def find_by_id(self, merchant_business_info_id):
        return _by_id_row()


def _query_handler() -> MerchantBusinessQueryHandler:
    return MerchantBusinessQueryHandler(FakeQueryService(), _logger())


async def test_query_find_all_formats_timestamps_and_drops_merchant_name() -> None:
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
    assert response.data[0].business_type == "Toko Elektronik"
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
        merchant_business_common_pb2.FindByIdMerchantBusinessRequest(id=1),
        FakeContext(),
    )
    assert response.message == "Successfully fetched merchant"
    assert response.data.id == 1
    assert response.data.business_type == "Toko Elektronik"
    # No nullable fields on this row -> zero values.
    assert response.data.tax_id == ""
    assert response.data.established_year == 0
    assert response.data.website_url == ""


async def test_query_find_by_id_zero_is_bad_request() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindById(
            merchant_business_common_pb2.FindByIdMerchantBusinessRequest(id=0),
            context,
        )
    # Unlike merchant_award (generic 500), merchant_business returns a
    # dedicated 400 invalid-id error.
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "Invalid merchant business ID"
    assert context.metadata


# ---- command handler ----


class FakeCommandService:
    def __init__(self) -> None:
        self.last_update: Any = None

    async def create(self, request):
        return CreateMerchantBusinessInformationRow(
            merchant_business_info_id=9,
            merchant_id=request.merchant_id,
            business_type=request.business_type,
            tax_id=request.tax_id,
            established_year=request.established_year,
            number_of_employees=request.number_of_employees,
            website_url=request.website_url or None,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.last_update = request
        return CreateMerchantBusinessInformationRow(
            merchant_business_info_id=request.merchant_business_info_id,
            merchant_id=10,
            business_type=request.business_type,
            tax_id=request.tax_id,
            established_year=request.established_year,
            number_of_employees=request.number_of_employees,
            website_url=request.website_url or None,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, merchant_business_info_id):
        return MerchantBusinessInformation(
            merchant_business_info_id=merchant_business_info_id,
            merchant_id=10,
            business_type="Toko Elektronik",
            tax_id=None,
            established_year=None,
            number_of_employees=None,
            website_url=None,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, merchant_business_info_id):
        return MerchantBusinessInformation(
            merchant_business_info_id=merchant_business_info_id,
            merchant_id=10,
            business_type="Toko Elektronik",
            tax_id=None,
            established_year=None,
            number_of_employees=None,
            website_url=None,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, merchant_business_info_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all(self):
        return True


def _command_handler(
    service: FakeCommandService | None = None,
) -> MerchantBusinessCommandHandler:
    return MerchantBusinessCommandHandler(service or FakeCommandService(), _logger())


def _create_pb(**overrides: Any) -> Any:
    values = {
        "merchant_id": 10,
        "business_type": "Toko Elektronik",
        "tax_id": "01.234.567.8-999.000",
        "established_year": 2010,
        "number_of_employees": 15,
        "website_url": "https://technostore.com",
    }
    values.update(overrides)
    return merchant_business_command_pb2.CreateMerchantBusinessRequest(**values)


def _update_pb(**overrides: Any) -> Any:
    values = {
        "merchant_business_info_id": 4,
        "business_type": "Retail Gadget",
        "tax_id": "04.567.890.1-666.000",
        "established_year": 2018,
        "number_of_employees": 8,
        "website_url": "https://gadgethub.com",
    }
    values.update(overrides)
    return merchant_business_command_pb2.UpdateMerchantBusinessRequest(**values)


async def test_command_create_success() -> None:
    response = await _command_handler().Create(_create_pb(), FakeContext())
    assert response.message == "Successfully created merchant business"
    assert response.data.id == 9
    assert response.data.created_at == "2026-01-02 03:04:05.000"
    assert response.data.established_year == 2010


async def test_command_create_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(_create_pb(business_type=""), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid create merchant business request"
    )


async def test_command_create_rejects_out_of_range_year() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(_create_pb(established_year=1800), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid create merchant business request"
    )


async def test_command_update_has_no_zero_id_guard() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).Update(
        _update_pb(merchant_business_info_id=0), FakeContext()
    )
    # handler forwards the request (the repository then answers 404).
    assert service.last_update is not None
    assert service.last_update.merchant_business_info_id == 0
    assert response.message == "Successfully updated merchant business"


async def test_command_update_success() -> None:
    response = await _command_handler().Update(_update_pb(), FakeContext())
    assert response.message == "Successfully updated merchant business"
    assert response.data.id == 4


async def test_command_update_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(_update_pb(business_type=""), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid update merchant business request"
    )


@pytest.mark.parametrize(
    "method_name",
    [
        "TrashedMerchantBusiness",
        "RestoreMerchantBusiness",
        "DeleteMerchantBusinessPermanent",
    ],
)
async def test_command_id_guards_reject_zero(method_name: str) -> None:
    context = FakeContext()
    handler = _command_handler()
    with pytest.raises(FakeAbort) as excinfo:
        await getattr(handler, method_name)(
            merchant_business_common_pb2.FindByIdMerchantBusinessRequest(id=0),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "Invalid merchant business ID"


async def test_command_trash_restore_return_delete_at_shape() -> None:
    trashed = await _command_handler().TrashedMerchantBusiness(
        merchant_business_common_pb2.FindByIdMerchantBusinessRequest(id=1),
        FakeContext(),
    )
    restored = await _command_handler().RestoreMerchantBusiness(
        merchant_business_common_pb2.FindByIdMerchantBusinessRequest(id=1),
        FakeContext(),
    )
    assert trashed.message == "Successfully trashed merchant business"
    assert trashed.data.deleted_at.value == "2026-02-01 05:06:07.000"
    assert restored.message == "Successfully restored merchant business"
    assert restored.data.HasField("deleted_at") is False


async def test_command_bulk_and_permanent_use_merchant_envelopes() -> None:
    handler = _command_handler()
    deleted = await handler.DeleteMerchantBusinessPermanent(
        merchant_business_common_pb2.FindByIdMerchantBusinessRequest(id=1),
        FakeContext(),
    )
    restored_all = await handler.RestoreAllMerchantBusiness(
        empty_pb2.Empty(), FakeContext()
    )
    deleted_all = await handler.DeleteAllMerchantBusinessPermanent(
        empty_pb2.Empty(), FakeContext()
    )
    assert isinstance(deleted, merchant_common_pb2.ApiResponseMerchantDelete)
    assert isinstance(restored_all, merchant_common_pb2.ApiResponseMerchantAll)
    assert isinstance(deleted_all, merchant_common_pb2.ApiResponseMerchantAll)
    assert deleted.message == "Successfully deleted merchant business permanently"
    assert (
        restored_all.message == "Successfully restored all trashed merchant businesses"
    )
    assert (
        deleted_all.message
        == "Successfully deleted all merchant businesses permanently"
    )


__all__ = []
