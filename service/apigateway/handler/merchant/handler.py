"""Gateway merchant handler: REST <-> merchant gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. Two handler structs (query + command) are merged into a single class, the review_detail/slider gateway the gateway also keeps a Redis response cache (`apigateway/cache/merchant`); deliberately does not, so every request goes straight to the merchant service, which serves its own cache. `Create`/`Update` take the owner id from the JWT (`request.state.user_id`, set by the auth middleware) and ignore the body `user_id`,. `UpdateStatus` exists on the gRPC service but the gateway exposes no route for it, so neither does."""

from __future__ import annotations

import grpc
from google.protobuf import empty_pb2

from pb.merchant import (
    merchant_command_pb2,
    merchant_command_pb2_grpc,
    merchant_common_pb2,
    merchant_query_pb2,
    merchant_query_pb2_grpc,
)
from service.apigateway.app.client import ServiceConnections
from shared.errors import err_unauthorized, new_bad_request_error, parse_grpc_error
from shared.mapper.merchant import (
    to_api_response_merchant,
    to_api_response_merchant_all,
    to_api_response_merchant_delete,
    to_api_response_merchant_delete_at,
    to_api_response_pagination_merchant,
    to_api_response_pagination_merchant_delete_at,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping. does not cap `page_size` here (unlike the request DTO validator), so does not either."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def require_positive_id(merchant_id: int) -> None:
    """Reject a non-positive path id before the gRPC hop (command routes). The gRPC handlers also guard `id == 0`, so this just fails one hop earlier with the same 400. gateway only guards the `strconv.Atoi` failure; adds the positive check as a deliberate cross-domain deviation. The query `find_by_id` route deliberately does NOT use this — forwards `id == 0` so the gRPC handler answers with `invalid merchant ID`."""
    if merchant_id <= 0:
        raise new_bad_request_error("Invalid ID")


class MerchantHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("merchant")
        self._query = merchant_query_pb2_grpc.MerchantQueryServiceStub(channel)
        self._command = merchant_command_pb2_grpc.MerchantCommandServiceStub(channel)

    # ---- query ----

    async def find_all(self, page: int, page_size: int, search: str):
        page, page_size = normalize_pagination(page, page_size)
        request = merchant_query_pb2.FindAllMerchantRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant(response)

    async def find_by_id(self, merchant_id: int):
        # No id guard — forwards 0 to gRPC, whose FindById guards `id == 0` and
        # returns 400 `invalid merchant ID`,.
        request = merchant_common_pb2.FindByIdMerchantRequest(id=merchant_id)
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant(response)

    async def find_by_active(self, page: int, page_size: int, search: str):
        page, page_size = normalize_pagination(page, page_size)
        request = merchant_query_pb2.FindAllMerchantRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_delete_at(response)

    async def find_by_trashed(self, page: int, page_size: int, search: str):
        page, page_size = normalize_pagination(page, page_size)
        request = merchant_query_pb2.FindAllMerchantRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_delete_at(response)

    # ---- command ----

    async def create(
        self,
        user_id: int | None,
        name: str,
        description: str,
        address: str,
        contact_email: str,
        contact_phone: str,
        status: str,
    ):
        if not user_id or user_id <= 0:
            raise err_unauthorized
        request = merchant_command_pb2.CreateMerchantRequest(
            user_id=user_id,
            name=name,
            description=description,
            address=address,
            contact_email=contact_email,
            contact_phone=contact_phone,
            status=status,
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant(response)

    async def update(
        self,
        merchant_id: int,
        user_id: int | None,
        name: str,
        description: str,
        address: str,
        contact_email: str,
        contact_phone: str,
        status: str,
    ):
        if not user_id or user_id <= 0:
            raise err_unauthorized
        require_positive_id(merchant_id)
        request = merchant_command_pb2.UpdateMerchantRequest(
            merchant_id=merchant_id,
            user_id=user_id,
            name=name,
            description=description,
            address=address,
            contact_email=contact_email,
            contact_phone=contact_phone,
            status=status,
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant(response)

    async def trash(self, merchant_id: int):
        require_positive_id(merchant_id)
        request = merchant_common_pb2.FindByIdMerchantRequest(id=merchant_id)
        try:
            response = await self._command.TrashedMerchant(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_delete_at(response)

    async def restore(self, merchant_id: int):
        require_positive_id(merchant_id)
        request = merchant_common_pb2.FindByIdMerchantRequest(id=merchant_id)
        try:
            response = await self._command.RestoreMerchant(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant(response)

    async def delete_permanent(self, merchant_id: int):
        require_positive_id(merchant_id)
        request = merchant_common_pb2.FindByIdMerchantRequest(id=merchant_id)
        try:
            response = await self._command.DeleteMerchantPermanent(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_delete(response)

    async def restore_all(self):
        try:
            response = await self._command.RestoreAllMerchant(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_all(response)

    async def delete_all_permanent(self):
        try:
            response = await self._command.DeleteAllMerchantPermanent(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_all(response)


__all__ = ["MerchantHandler", "normalize_pagination", "require_positive_id"]
