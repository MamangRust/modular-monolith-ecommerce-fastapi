"""Gateway merchant_award handler: REST <-> merchant_award gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. the gateway keeps a Redis response cache (`apigateway/cache/merchant_awards`); deliberately does not, so every request goes straight to the merchant_award service, which serves its own cache. Every path-id route guards `id <= 0` with 400 `Invalid ID` (including the query `find_by_id`, matching — unlike merchant_detail, whose query route uses `id is required`). `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` reuse the merchant envelope (`pb.merchant` `ApiResponseMerchantDelete`/`All`), exactly."""

from __future__ import annotations

import grpc
from google.protobuf import empty_pb2

from pb.merchant import merchant_query_pb2
from pb.merchant_award import (
    merchant_award_command_pb2,
    merchant_award_command_pb2_grpc,
    merchant_award_common_pb2,
    merchant_award_query_pb2_grpc,
)
from service.apigateway.app.client import ServiceConnections
from shared.errors import new_bad_request_error, parse_grpc_error
from shared.mapper.merchant import (
    to_api_response_merchant_all,
    to_api_response_merchant_delete,
)
from shared.mapper.merchant_award import (
    to_api_response_merchant_award,
    to_api_response_merchant_award_delete_at,
    to_api_response_pagination_merchant_award,
    to_api_response_pagination_merchant_award_delete_at,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping. does not cap `page_size` here (unlike the request DTO validator), so not either."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def require_positive_id(merchant_certification_id: int) -> None:
    """Reject a non-positive path id before the gRPC hop. guards `id <= 0` on every merchant_award route (query and command) with the message `Invalid ID`; fails one hop earlier with the same 400."""
    if merchant_certification_id <= 0:
        raise new_bad_request_error("Invalid ID")


def _list_request(page: int, page_size: int, search: str):
    """The three list RPCs take the shared `FindAllMerchantRequest`."""
    return merchant_query_pb2.FindAllMerchantRequest(
        page=page, page_size=page_size, search=search or ""
    )


class MerchantAwardHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("merchant_award")
        self._query = merchant_award_query_pb2_grpc.MerchantAwardQueryServiceStub(
            channel
        )
        self._command = (
            merchant_award_command_pb2_grpc.MerchantAwardCommandServiceStub(channel)
        )

    # ---- query ----

    async def find_all(self, page: int, page_size: int, search: str):
        page, page_size = normalize_pagination(page, page_size)
        try:
            response = await self._query.FindAll(
                _list_request(page, page_size, search), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_award(response)

    async def find_by_id(self, merchant_certification_id: int):
        require_positive_id(merchant_certification_id)
        request = merchant_award_common_pb2.FindByIdMerchantAwardRequest(
            id=merchant_certification_id
        )
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_award(response)

    async def find_by_active(self, page: int, page_size: int, search: str):
        page, page_size = normalize_pagination(page, page_size)
        try:
            response = await self._query.FindByActive(
                _list_request(page, page_size, search), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_award_delete_at(response)

    async def find_by_trashed(self, page: int, page_size: int, search: str):
        page, page_size = normalize_pagination(page, page_size)
        try:
            response = await self._query.FindByTrashed(
                _list_request(page, page_size, search), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_award_delete_at(response)

    # ---- command ----

    async def create(
        self,
        merchant_id: int,
        title: str,
        description: str,
        issued_by: str,
        issue_date: str,
        expiry_date: str,
        certificate_url: str,
    ):
        request = merchant_award_command_pb2.CreateMerchantAwardRequest(
            merchant_id=merchant_id,
            title=title,
            description=description,
            issued_by=issued_by,
            issue_date=issue_date,
            expiry_date=expiry_date,
            certificate_url=certificate_url,
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_award(response)

    async def update(
        self,
        merchant_certification_id: int,
        title: str,
        description: str,
        issued_by: str,
        issue_date: str,
        expiry_date: str,
        certificate_url: str,
    ):
        require_positive_id(merchant_certification_id)
        request = merchant_award_command_pb2.UpdateMerchantAwardRequest(
            merchant_certification_id=merchant_certification_id,
            title=title,
            description=description,
            issued_by=issued_by,
            issue_date=issue_date,
            expiry_date=expiry_date,
            certificate_url=certificate_url,
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_award(response)

    async def trash(self, merchant_certification_id: int):
        require_positive_id(merchant_certification_id)
        request = merchant_award_common_pb2.FindByIdMerchantAwardRequest(
            id=merchant_certification_id
        )
        try:
            response = await self._command.TrashedMerchantAward(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_award_delete_at(response)

    async def restore(self, merchant_certification_id: int):
        require_positive_id(merchant_certification_id)
        request = merchant_award_common_pb2.FindByIdMerchantAwardRequest(
            id=merchant_certification_id
        )
        try:
            response = await self._command.RestoreMerchantAward(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        # returns the DeleteAt envelope on restore too.
        return to_api_response_merchant_award_delete_at(response)

    async def delete_permanent(self, merchant_certification_id: int):
        require_positive_id(merchant_certification_id)
        request = merchant_award_common_pb2.FindByIdMerchantAwardRequest(
            id=merchant_certification_id
        )
        try:
            response = await self._command.DeleteMerchantAwardPermanent(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_delete(response)

    async def restore_all(self):
        try:
            response = await self._command.RestoreAllMerchantAward(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_all(response)

    async def delete_all_permanent(self):
        try:
            response = await self._command.DeleteAllMerchantAwardPermanent(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_all(response)


__all__ = ["MerchantAwardHandler", "normalize_pagination", "require_positive_id"]
