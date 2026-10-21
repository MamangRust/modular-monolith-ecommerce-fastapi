"""Unit tests for the merchant_policy gRPC handlers. All timestamps are emitted as `%Y-%m-%d %H:%M:%S.mmm`. Unlike merchant_business, the merchant_policy mapping DOES copy the joined `merchant_name` for the list rows (but not for the single/command rows)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.merchant import merchant_common_pb2, merchant_query_pb2
from pb.merchant_policy import (
    merchant_policy_command_pb2,
    merchant_policy_common_pb2,
)
from pkg.database.schema.merchant_policy import (
    CreateMerchantPolicyRow,
    GetMerchantPoliciesActiveRow,
    GetMerchantPoliciesRow,
    GetMerchantPolicyRow,
    MerchantPolicy,
)
from pkg.logger.logger import Logger
from service.merchant_policy.handler.merchant_policy_command import (
    MerchantPolicyCommandHandler,
)
from service.merchant_policy.handler.merchant_policy_query import (
    MerchantPolicyQueryHandler,
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


def _list_row(policy_id: int = 1, total: int = 11) -> GetMerchantPoliciesRow:
    return GetMerchantPoliciesRow(
        merchant_policy_id=policy_id,
        merchant_id=10,
        policy_type="Shipping",
        title="Free Shipping on Orders Above $50",
        description="desc",
        created_at=CREATED,
        updated_at=UPDATED,
        merchant_name="Elektronik Store",
        total_count=total,
    )


def _active_row(deleted_at: datetime | None = None) -> GetMerchantPoliciesActiveRow:
    return GetMerchantPoliciesActiveRow(
        merchant_policy_id=1,
        merchant_id=10,
        policy_type="Refund",
        title="30-Day Refund Policy",
        description="desc",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        merchant_name="Elektronik Store",
        total_count=1,
    )


def _by_id_row() -> GetMerchantPolicyRow:
    return GetMerchantPolicyRow(
        merchant_policy_id=1,
        merchant_id=10,
        policy_type="Shipping",
        title="Free Shipping on Orders Above $50",
        description="desc",
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

    async def find_by_id(self, merchant_policy_id):
        return _by_id_row()


def _query_handler() -> MerchantPolicyQueryHandler:
    return MerchantPolicyQueryHandler(FakeQueryService(), _logger())


async def test_query_find_all_formats_timestamps_and_copies_merchant_name() -> None:
    response = await _query_handler().FindAll(
        merchant_query_pb2.FindAllMerchantRequest(page=0, page_size=0),
        FakeContext(),
    )
    assert response.message == "Successfully fetched merchant policies"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_records == 11
    assert response.data[0].created_at == "2026-01-02 03:04:05.000"
    assert response.data[0].updated_at == "2026-01-03 04:05:06.000"
    assert response.data[0].policy_type == "Shipping"
    # Unlike merchant_business, fills merchant_name for list rows.
    assert response.data[0].merchant_name == "Elektronik Store"


async def test_query_find_by_active_omits_deleted_at_wrapper_when_null() -> None:
    response = await _query_handler().FindByActive(
        merchant_query_pb2.FindAllMerchantRequest(page=1, page_size=10),
        FakeContext(),
    )
    assert response.message == "Successfully fetched merchant policies"
    assert response.data[0].HasField("deleted_at") is False


async def test_query_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        merchant_query_pb2.FindAllMerchantRequest(page=1, page_size=10),
        FakeContext(),
    )
    assert response.data[0].HasField("deleted_at") is True
    assert response.data[0].deleted_at.value == "2026-02-01 05:06:07.000"


async def test_query_find_by_id_success() -> None:
    response = await _query_handler().FindById(
        merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=1),
        FakeContext(),
    )
    assert response.message == "Successfully fetched merchant policy"
    assert response.data.id == 1
    assert response.data.policy_type == "Shipping"
    # The single-row projection has no merchant_name.
    assert response.data.merchant_name == ""


async def test_query_find_by_id_zero_is_bad_request() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindById(
            merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=0),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid merchant policy id"
    assert context.metadata


# ---- command handler ----


class FakeCommandService:
    def __init__(self) -> None:
        self.last_update: Any = None

    async def create(self, request):
        return CreateMerchantPolicyRow(
            merchant_policy_id=9,
            merchant_id=request.merchant_id,
            policy_type=request.policy_type,
            title=request.title,
            description=request.description,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.last_update = request
        return CreateMerchantPolicyRow(
            merchant_policy_id=request.merchant_policy_id,
            merchant_id=10,
            policy_type=request.policy_type,
            title=request.title,
            description=request.description,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, merchant_policy_id):
        return MerchantPolicy(
            merchant_policy_id=merchant_policy_id,
            merchant_id=10,
            policy_type="Shipping",
            title="Free Shipping",
            description="desc",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, merchant_policy_id):
        return MerchantPolicy(
            merchant_policy_id=merchant_policy_id,
            merchant_id=10,
            policy_type="Shipping",
            title="Free Shipping",
            description="desc",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, merchant_policy_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all(self):
        return True


def _command_handler(
    service: FakeCommandService | None = None,
) -> MerchantPolicyCommandHandler:
    return MerchantPolicyCommandHandler(service or FakeCommandService(), _logger())


def _create_pb(**overrides: Any) -> Any:
    values = {
        "merchant_id": 10,
        "policy_type": "Shipping",
        "title": "Free Shipping on Orders Above $50",
        "description": "desc",
    }
    values.update(overrides)
    return merchant_policy_command_pb2.CreateMerchantPoliciesRequest(**values)


def _update_pb(**overrides: Any) -> Any:
    values = {
        "merchant_policy_id": 4,
        "policy_type": "Refund",
        "title": "30-Day Refund Policy",
        "description": "desc",
    }
    values.update(overrides)
    return merchant_policy_command_pb2.UpdateMerchantPoliciesRequest(**values)


async def test_command_create_success() -> None:
    response = await _command_handler().Create(_create_pb(), FakeContext())
    assert response.message == "Successfully created merchant policy"
    assert response.data.id == 9
    assert response.data.created_at == "2026-01-02 03:04:05.000"
    assert response.data.policy_type == "Shipping"


async def test_command_create_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(_create_pb(policy_type=""), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid create merchant policy request"
    )


async def test_command_create_rejects_zero_merchant_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(_create_pb(merchant_id=0), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid create merchant policy request"
    )


async def test_command_update_has_no_zero_id_guard() -> None:
    service = FakeCommandService()
    response = await _command_handler(service).Update(
        _update_pb(merchant_policy_id=0), FakeContext()
    )
    assert service.last_update is not None
    assert service.last_update.merchant_policy_id == 0
    assert response.message == "Successfully updated merchant policy"


async def test_command_update_success() -> None:
    response = await _command_handler().Update(_update_pb(), FakeContext())
    assert response.message == "Successfully updated merchant policy"
    assert response.data.id == 4


async def test_command_update_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(_update_pb(title=""), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid update merchant policy request"
    )


@pytest.mark.parametrize(
    "method_name",
    [
        "TrashedMerchantPolicies",
        "RestoreMerchantPolicies",
        "DeleteMerchantPoliciesPermanent",
    ],
)
async def test_command_id_guards_reject_zero(method_name: str) -> None:
    context = FakeContext()
    handler = _command_handler()
    with pytest.raises(FakeAbort) as excinfo:
        await getattr(handler, method_name)(
            merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=0),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid merchant policy id"


async def test_command_trash_restore_return_delete_at_shape() -> None:
    trashed = await _command_handler().TrashedMerchantPolicies(
        merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=1),
        FakeContext(),
    )
    restored = await _command_handler().RestoreMerchantPolicies(
        merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=1),
        FakeContext(),
    )
    assert trashed.message == "Successfully processed merchant policy"
    assert trashed.data.deleted_at.value == "2026-02-01 05:06:07.000"
    assert restored.message == "Successfully processed merchant policy"
    assert restored.data.HasField("deleted_at") is False


async def test_command_bulk_and_permanent_use_merchant_envelopes() -> None:
    handler = _command_handler()
    deleted = await handler.DeleteMerchantPoliciesPermanent(
        merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(id=1),
        FakeContext(),
    )
    restored_all = await handler.RestoreAllMerchantPolicies(
        empty_pb2.Empty(), FakeContext()
    )
    deleted_all = await handler.DeleteAllMerchantPoliciesPermanent(
        empty_pb2.Empty(), FakeContext()
    )
    assert isinstance(deleted, merchant_common_pb2.ApiResponseMerchantDelete)
    assert isinstance(restored_all, merchant_common_pb2.ApiResponseMerchantAll)
    assert isinstance(deleted_all, merchant_common_pb2.ApiResponseMerchantAll)
    assert deleted.message == "Successfully deleted merchant policy permanently"
    assert restored_all.message == "Successfully restored all merchant policies"
    assert (
        deleted_all.message
        == "Successfully deleted all merchant policies permanently"
    )


__all__ = []
