"""Unit tests for the merchant_detail + merchant_social_link gRPC handlers. Timestamps are emitted as `%Y-%m-%d %H:%M:%S.mmm` (— a new format for this domain). `FindById` and every id-carrying command guard `id == 0` with a 400 `invalid merchant detail ID`. `Create`/`Update` validation failures raise the sentinels verbatim. The command `DeletePermanent`/`RestoreAll`/`DeleteAll` responses reuse the merchant envelopes (`pb.merchant`). The proto `social_media_links` field is never filled (ignores the column)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import grpc
import pytest
from google.protobuf import empty_pb2

from pb.merchant import merchant_common_pb2
from pb.merchant_detail import (
    merchant_detail_command_pb2,
    merchant_detail_common_pb2,
    merchant_detail_query_pb2,
)
from pb.merchant_social_link import merchant_social_link_command_pb2
from pkg.database.schema.merchant_detail import (
    CreateMerchantDetailRow,
    CreateMerchantSocialMediaLinkRow,
    GetMerchantDetailRow,
    GetMerchantDetailsActiveRow,
    GetMerchantDetailsRow,
    MerchantDetail,
)
from pkg.logger.logger import Logger
from service.merchant_detail.handler.merchant_detail_command import (
    MerchantDetailCommandHandler,
)
from service.merchant_detail.handler.merchant_detail_query import (
    MerchantDetailQueryHandler,
)
from service.merchant_detail.handler.merchant_social_link_command import (
    MerchantSocialLinkCommandHandler,
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


def _list_row(detail_id: int = 1, total: int = 11) -> GetMerchantDetailsRow:
    return GetMerchantDetailsRow(
        merchant_detail_id=detail_id,
        merchant_id=10,
        display_name="Techno Store",
        cover_image_url="cover/techno.jpg",
        logo_url="logo/techno.png",
        short_description="desc",
        website_url="https://technostore.com",
        created_at=CREATED,
        updated_at=UPDATED,
        merchant_name="Elektronik Store",
        total_count=total,
        social_media_links=None,
    )


def _active_row(deleted_at: datetime | None = None) -> GetMerchantDetailsActiveRow:
    return GetMerchantDetailsActiveRow(
        merchant_detail_id=1,
        merchant_id=10,
        display_name="Techno Store",
        cover_image_url=None,
        logo_url=None,
        short_description=None,
        website_url=None,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        merchant_name="Elektronik Store",
        total_count=1,
        social_media_links=None,
    )


def _by_id_row() -> GetMerchantDetailRow:
    return GetMerchantDetailRow(
        merchant_detail_id=1,
        merchant_id=10,
        display_name="Techno Store",
        cover_image_url=None,
        logo_url=None,
        short_description=None,
        website_url=None,
        created_at=CREATED,
        updated_at=UPDATED,
        merchant_name="Elektronik Store",
        social_media_links=None,
    )


class FakeQueryService:
    async def find_all(self, search, page, page_size):
        return [_list_row()], 11

    async def find_active(self, search, page, page_size):
        return [_active_row()], 1

    async def find_trashed(self, search, page, page_size):
        return [_active_row(deleted_at=DELETED)], 1

    async def find_by_id(self, merchant_detail_id):
        return _by_id_row()


def _query_handler() -> MerchantDetailQueryHandler:
    return MerchantDetailQueryHandler(FakeQueryService(), _logger())


async def test_query_find_all_timestamp_format() -> None:
    response = await _query_handler().FindAll(
        merchant_detail_query_pb2.FindAllMerchantDetailRequest(page=0, page_size=0),
        FakeContext(),
    )
    assert response.message == "Successfully fetched merchant details"
    assert response.pagination.current_page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_records == 11
    assert response.data[0].created_at == "2026-01-02 03:04:05.000"
    assert response.data[0].updated_at == "2026-01-03 04:05:06.000"


async def test_query_find_all_never_fills_social_links() -> None:
    response = await _query_handler().FindAll(
        merchant_detail_query_pb2.FindAllMerchantDetailRequest(page=1, page_size=10),
        FakeContext(),
    )
    # ignores the SocialMediaLinks column, so the wire list is always empty.
    assert len(response.data[0].social_media_links) == 0


async def test_query_find_by_active_omits_deleted_at_wrapper_when_null() -> None:
    response = await _query_handler().FindByActive(
        merchant_detail_query_pb2.FindAllMerchantDetailRequest(page=1, page_size=10),
        FakeContext(),
    )
    assert response.message == "Successfully fetched active merchant details"
    assert response.data[0].HasField("deleted_at") is False


async def test_query_find_by_trashed_includes_deleted_at() -> None:
    response = await _query_handler().FindByTrashed(
        merchant_detail_query_pb2.FindAllMerchantDetailRequest(page=1, page_size=10),
        FakeContext(),
    )
    assert response.message == "Successfully fetched trashed merchant details"
    assert response.data[0].HasField("deleted_at") is True
    assert response.data[0].deleted_at.value == "2026-02-01 05:06:07.000"


async def test_query_find_by_id_success() -> None:
    response = await _query_handler().FindById(
        merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=1), FakeContext()
    )
    assert response.message == "Successfully fetched merchant detail"
    assert response.data.id == 1


async def test_query_find_by_id_rejects_zero() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _query_handler().FindById(
            merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=0), context
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid merchant detail ID"
    assert context.metadata


# ---- command handler ----


class FakeCommandService:
    async def create(self, request):
        return CreateMerchantDetailRow(
            merchant_detail_id=9,
            merchant_id=request.merchant_id,
            display_name=request.display_name,
            cover_image_url=request.cover_image_url,
            logo_url=request.logo_url,
            short_description=request.short_description,
            website_url=request.website_url,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        return CreateMerchantDetailRow(
            merchant_detail_id=request.merchant_detail_id or 1,
            merchant_id=10,
            display_name=request.display_name,
            cover_image_url=request.cover_image_url,
            logo_url=request.logo_url,
            short_description=request.short_description,
            website_url=request.website_url,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, merchant_detail_id):
        return MerchantDetail(
            merchant_detail_id=merchant_detail_id,
            merchant_id=10,
            display_name="N",
            cover_image_url=None,
            logo_url=None,
            short_description=None,
            website_url=None,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, merchant_detail_id):
        return MerchantDetail(
            merchant_detail_id=merchant_detail_id,
            merchant_id=10,
            display_name="N",
            cover_image_url=None,
            logo_url=None,
            short_description=None,
            website_url=None,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, merchant_detail_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all(self):
        return True


def _command_handler() -> MerchantDetailCommandHandler:
    return MerchantDetailCommandHandler(FakeCommandService(), _logger())


def _create_pb(**overrides: Any) -> Any:
    values = {
        "merchant_id": 10,
        "display_name": "Techno Store",
        "cover_image_url": "c",
        "logo_url": "l",
        "short_description": "d",
        "website_url": "https://technostore.com",
    }
    values.update(overrides)
    return merchant_detail_command_pb2.CreateMerchantDetailRequest(**values)


async def test_command_create_success() -> None:
    response = await _command_handler().Create(_create_pb(), FakeContext())
    assert response.message == "Successfully created merchant detail"
    assert response.data.id == 9
    assert response.data.created_at == "2026-01-02 03:04:05.000"


async def test_command_create_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Create(_create_pb(display_name=""), context)
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid create merchant detail request"
    )


async def test_command_update_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(
            merchant_detail_command_pb2.UpdateMerchantDetailRequest(
                merchant_detail_id=0,
                display_name="N",
                short_description="d",
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid merchant detail ID"


async def test_command_update_success() -> None:
    response = await _command_handler().Update(
        merchant_detail_command_pb2.UpdateMerchantDetailRequest(
            merchant_detail_id=1,
            display_name="N",
            cover_image_url="c",
            logo_url="l",
            short_description="d",
            website_url="https://x.com",
        ),
        FakeContext(),
    )
    assert response.message == "Successfully updated merchant detail"
    assert response.data.id == 1


async def test_command_update_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _command_handler().Update(
            merchant_detail_command_pb2.UpdateMerchantDetailRequest(
                merchant_detail_id=1,
                display_name="N",
                short_description="",  # invalid: required
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid update merchant detail request"
    )


async def test_command_trash_restore_return_delete_at_shape() -> None:
    trashed = await _command_handler().TrashedMerchantDetail(
        merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=1), FakeContext()
    )
    restored = await _command_handler().RestoreMerchantDetail(
        merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=1), FakeContext()
    )
    assert trashed.message == "Successfully trashed merchant detail"
    assert trashed.data.deleted_at.value == "2026-02-01 05:06:07.000"
    assert restored.message == "Successfully restored merchant detail"
    assert restored.data.HasField("deleted_at") is False


async def test_command_bulk_and_permanent_use_merchant_envelopes() -> None:
    deleted = await _command_handler().DeleteMerchantDetailPermanent(
        merchant_detail_common_pb2.FindByIdMerchantDetailRequest(id=1), FakeContext()
    )
    restored_all = await _command_handler().RestoreAllMerchantDetail(
        empty_pb2.Empty(), FakeContext()
    )
    deleted_all = await _command_handler().DeleteAllMerchantDetailPermanent(
        empty_pb2.Empty(), FakeContext()
    )
    # The response types are the merchant envelopes, not merchant_detail_*.
    assert isinstance(deleted, merchant_common_pb2.ApiResponseMerchantDelete)
    assert isinstance(restored_all, merchant_common_pb2.ApiResponseMerchantAll)
    assert isinstance(deleted_all, merchant_common_pb2.ApiResponseMerchantAll)
    assert deleted.message == "Successfully deleted merchant detail permanently"
    assert restored_all.message == "Successfully restored all merchant details"
    assert (
        deleted_all.message
        == "Successfully deleted all merchant details permanently"
    )


# ---- social link command handler ----


class FakeSocialService:
    async def create(self, request):
        return CreateMerchantSocialMediaLinkRow(
            merchant_social_id=1,
            merchant_detail_id=request.merchant_detail_id,
            platform=request.platform,
            url=request.url,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        return CreateMerchantSocialMediaLinkRow(
            merchant_social_id=request.id,
            merchant_detail_id=request.merchant_detail_id,
            platform=request.platform,
            url=request.url,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, social_id):
        return True

    async def restore(self, social_id):
        return True

    async def delete_permanent(self, social_id):
        return True

    async def restore_all(self):
        return True

    async def delete_all(self):
        return True


def _social_handler() -> MerchantSocialLinkCommandHandler:
    return MerchantSocialLinkCommandHandler(FakeSocialService(), _logger())


async def test_social_create_success() -> None:
    response = await _social_handler().Create(
        merchant_social_link_command_pb2.CreateMerchantSocialRequest(
            merchant_detail_id=1,
            platform="Facebook",
            url="https://facebook.com/merchant1",
        ),
        FakeContext(),
    )
    assert response.message == "Successfully created merchant social link"
    assert response.data.id == 1
    assert response.data.platform == "Facebook"
    # The gRPC mapping DOES fill created_at/updated_at on the proto (the gateway
    # command mapper ignores them mapper test).
    assert response.data.created_at == "2026-01-02 03:04:05.000"


async def test_social_create_validation_failure() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _social_handler().Create(
            merchant_social_link_command_pb2.CreateMerchantSocialRequest(
                merchant_detail_id=1,
                platform="",  # invalid: required
                url="https://facebook.com/merchant1",
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert (
        excinfo.value.message
        == "Validation failed: invalid create merchant detail request"
    )


async def test_social_update_rejects_zero_id() -> None:
    context = FakeContext()
    with pytest.raises(FakeAbort) as excinfo:
        await _social_handler().Update(
            merchant_social_link_command_pb2.UpdateMerchantSocialRequest(
                id=0,
                merchant_detail_id=1,
                platform="Facebook",
                url="https://facebook.com/merchant1",
            ),
            context,
        )
    assert excinfo.value.code is grpc.StatusCode.INVALID_ARGUMENT
    assert excinfo.value.message == "invalid merchant detail ID"


async def test_social_update_success() -> None:
    response = await _social_handler().Update(
        merchant_social_link_command_pb2.UpdateMerchantSocialRequest(
            id=5,
            merchant_detail_id=1,
            platform="Twitter",
            url="https://twitter.com/merchant1",
        ),
        FakeContext(),
    )
    assert response.message == "Successfully updated merchant social link"
    assert response.data.id == 5


__all__ = []
