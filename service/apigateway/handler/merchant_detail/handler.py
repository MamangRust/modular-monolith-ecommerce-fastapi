"""Gateway merchant_detail handler: REST <-> merchant_detail gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. the gateway keeps a Redis response cache (`apigateway/cache/merchant_detail`); deliberately does not, so every request goes straight to the merchant_detail service, which serves its own cache. `Create` takes no owner id (unlike merchant, whose create pulls `user_id` from the JWT) — the merchant detail body has no user field, so there is no 401 path here. The command `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` responses reuse the merchant envelope (`pb.merchant` `ApiResponseMerchantDelete`/`All`),, which borrows `merchantMapper.ToApiResponseMerchantDelete`/`All`."""

from __future__ import annotations

import grpc
from google.protobuf import empty_pb2

from pb.merchant_detail import (
    merchant_detail_command_pb2,
    merchant_detail_command_pb2_grpc,
    merchant_detail_common_pb2,
    merchant_detail_query_pb2,
    merchant_detail_query_pb2_grpc,
)
from service.apigateway.app.client import ServiceConnections
from shared.errors import new_bad_request_error, parse_grpc_error
from shared.mapper.merchant import (
    to_api_response_merchant_all,
    to_api_response_merchant_delete,
)
from shared.mapper.merchant_detail import (
    to_api_response_merchant_detail,
    to_api_response_merchant_detail_delete_at,
    to_api_response_merchant_detail_relation,
    to_api_response_pagination_merchant_detail,
    to_api_response_pagination_merchant_detail_delete_at,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping. does not cap `page_size` here (unlike the request DTO validator), so does not either."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def require_positive_id(merchant_detail_id: int) -> None:
    """Reject a non-positive path id before the gRPC hop (command routes). The gRPC handlers also guard `id == 0`, so this just fails one hop earlier with the same 400. gateway only guards the `strconv.Atoi` failure; adds the positive check as a deliberate cross-domain deviation. The query `find_by_id` route uses the message `id is required` instead — see `find_by_id`."""
    if merchant_detail_id <= 0:
        raise new_bad_request_error("Invalid ID")


class MerchantDetailHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("merchant_detail")
        self._query = merchant_detail_query_pb2_grpc.MerchantDetailQueryServiceStub(
            channel
        )
        self._command = (
            merchant_detail_command_pb2_grpc.MerchantDetailCommandServiceStub(channel)
        )

    # ---- query ----

    async def find_all(self, page: int, page_size: int, search: str):
        page, page_size = normalize_pagination(page, page_size)
        request = merchant_detail_query_pb2.FindAllMerchantDetailRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_detail(response)

    async def find_by_id(self, merchant_detail_id: int):
        # gateway guards `id <= 0` here with `id is required` (BEDA dari
        # merchant, yang meneruskan 0 ke gRPC). The gRPC handler guards too, but
        # the gateway answers first with this message.
        if merchant_detail_id <= 0:
            raise new_bad_request_error("id is required")
        request = merchant_detail_common_pb2.FindByIdMerchantDetailRequest(
            id=merchant_detail_id
        )
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_detail_relation(response)

    async def find_by_active(self, page: int, page_size: int, search: str):
        page, page_size = normalize_pagination(page, page_size)
        request = merchant_detail_query_pb2.FindAllMerchantDetailRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_detail_delete_at(response)

    async def find_by_trashed(self, page: int, page_size: int, search: str):
        page, page_size = normalize_pagination(page, page_size)
        request = merchant_detail_query_pb2.FindAllMerchantDetailRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_detail_delete_at(response)

    # ---- command ----

    async def create(
        self,
        merchant_id: int,
        display_name: str,
        cover_image_url: str,
        logo_url: str,
        short_description: str,
        website_url: str,
    ):
        request = merchant_detail_command_pb2.CreateMerchantDetailRequest(
            merchant_id=merchant_id,
            display_name=display_name,
            cover_image_url=cover_image_url,
            logo_url=logo_url,
            short_description=short_description,
            website_url=website_url,
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_detail(response)

    async def update(
        self,
        merchant_detail_id: int,
        display_name: str,
        cover_image_url: str,
        logo_url: str,
        short_description: str,
        website_url: str,
    ):
        require_positive_id(merchant_detail_id)
        request = merchant_detail_command_pb2.UpdateMerchantDetailRequest(
            merchant_detail_id=merchant_detail_id,
            display_name=display_name,
            cover_image_url=cover_image_url,
            logo_url=logo_url,
            short_description=short_description,
            website_url=website_url,
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_detail(response)

    async def trash(self, merchant_detail_id: int):
        require_positive_id(merchant_detail_id)
        request = merchant_detail_common_pb2.FindByIdMerchantDetailRequest(
            id=merchant_detail_id
        )
        try:
            response = await self._command.TrashedMerchantDetail(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_detail_delete_at(response)

    async def restore(self, merchant_detail_id: int):
        require_positive_id(merchant_detail_id)
        request = merchant_detail_common_pb2.FindByIdMerchantDetailRequest(
            id=merchant_detail_id
        )
        try:
            response = await self._command.RestoreMerchantDetail(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        # returns the DeleteAt envelope on restore too (not the plain detail).
        return to_api_response_merchant_detail_delete_at(response)

    async def delete_permanent(self, merchant_detail_id: int):
        require_positive_id(merchant_detail_id)
        request = merchant_detail_common_pb2.FindByIdMerchantDetailRequest(
            id=merchant_detail_id
        )
        try:
            response = await self._command.DeleteMerchantDetailPermanent(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_delete(response)

    async def restore_all(self):
        try:
            response = await self._command.RestoreAllMerchantDetail(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_all(response)

    async def delete_all_permanent(self):
        try:
            response = await self._command.DeleteAllMerchantDetailPermanent(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_all(response)


__all__ = ["MerchantDetailHandler", "normalize_pagination", "require_positive_id"]
