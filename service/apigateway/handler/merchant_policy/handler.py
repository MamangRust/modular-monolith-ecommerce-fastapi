"""Gateway merchant_policy handler: REST <-> merchant_policy gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. the gateway keeps a Redis response cache (`apigateway/cache/merchant_policies`) and evicts it with a literal `0` on Update/Trash/Restore/DeletePermanent; deliberately does not cache in the gateway, so every request goes straight to the merchant_policy service, which serves its own cache. Every path-id route guards `id <= 0` with 400 `Invalid ID` (including the query `find_by_id`, matching). `DeletePermanent`/`RestoreAll`/`DeleteAllPermanent` reuse the merchant envelope (`pb.merchant` `ApiResponseMerchantDelete`/`All`),."""

from __future__ import annotations

import grpc
from google.protobuf import empty_pb2

from pb.merchant import merchant_query_pb2
from pb.merchant_policy import (
    merchant_policy_command_pb2,
    merchant_policy_command_pb2_grpc,
    merchant_policy_common_pb2,
    merchant_policy_query_pb2_grpc,
)
from service.apigateway.app.client import ServiceConnections
from shared.errors import new_bad_request_error, parse_grpc_error
from shared.mapper.merchant import (
    to_api_response_merchant_all,
    to_api_response_merchant_delete,
)
from shared.mapper.merchant_policy import (
    to_api_response_merchant_policy,
    to_api_response_merchant_policy_delete_at,
    to_api_response_pagination_merchant_policies,
    to_api_response_pagination_merchant_policies_delete_at,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping. does not cap `page_size` here (unlike the request DTO validator), so does not either."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def require_positive_id(merchant_policy_id: int) -> None:
    """Reject a non-positive path id before the gRPC hop. guards `id <= 0` on every merchant_policy route (query and command) with the message `Invalid ID`; fails one hop earlier with the same 400."""
    if merchant_policy_id <= 0:
        raise new_bad_request_error("Invalid ID")


def _list_request(page: int, page_size: int, search: str):
    """The three list RPCs take the shared `FindAllMerchantRequest`."""
    return merchant_query_pb2.FindAllMerchantRequest(
        page=page, page_size=page_size, search=search or ""
    )


class MerchantPolicyHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("merchant_policy")
        self._query = (
            merchant_policy_query_pb2_grpc.MerchantPolicyQueryServiceStub(channel)
        )
        self._command = (
            merchant_policy_command_pb2_grpc.MerchantPolicyCommandServiceStub(channel)
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
        return to_api_response_pagination_merchant_policies(response)

    async def find_by_id(self, merchant_policy_id: int):
        require_positive_id(merchant_policy_id)
        request = merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(
            id=merchant_policy_id
        )
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_policy(response)

    async def find_by_active(self, page: int, page_size: int, search: str):
        page, page_size = normalize_pagination(page, page_size)
        try:
            response = await self._query.FindByActive(
                _list_request(page, page_size, search), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_policies_delete_at(response)

    async def find_by_trashed(self, page: int, page_size: int, search: str):
        page, page_size = normalize_pagination(page, page_size)
        try:
            response = await self._query.FindByTrashed(
                _list_request(page, page_size, search), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_merchant_policies_delete_at(response)

    # ---- command ----

    async def create(
        self,
        merchant_id: int,
        policy_type: str,
        title: str,
        description: str,
    ):
        request = merchant_policy_command_pb2.CreateMerchantPoliciesRequest(
            merchant_id=merchant_id,
            policy_type=policy_type,
            title=title,
            description=description,
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_policy(response)

    async def update(
        self,
        merchant_policy_id: int,
        policy_type: str,
        title: str,
        description: str,
    ):
        require_positive_id(merchant_policy_id)
        request = merchant_policy_command_pb2.UpdateMerchantPoliciesRequest(
            merchant_policy_id=merchant_policy_id,
            policy_type=policy_type,
            title=title,
            description=description,
        )
        try:
            response = await self._command.Update(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_policy(response)

    async def trash(self, merchant_policy_id: int):
        require_positive_id(merchant_policy_id)
        request = merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(
            id=merchant_policy_id
        )
        try:
            response = await self._command.TrashedMerchantPolicies(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_policy_delete_at(response)

    async def restore(self, merchant_policy_id: int):
        require_positive_id(merchant_policy_id)
        request = merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(
            id=merchant_policy_id
        )
        try:
            response = await self._command.RestoreMerchantPolicies(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        # returns the DeleteAt envelope on restore too.
        return to_api_response_merchant_policy_delete_at(response)

    async def delete_permanent(self, merchant_policy_id: int):
        require_positive_id(merchant_policy_id)
        request = merchant_policy_common_pb2.FindByIdMerchantPoliciesRequest(
            id=merchant_policy_id
        )
        try:
            response = await self._command.DeleteMerchantPoliciesPermanent(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_delete(response)

    async def restore_all(self):
        try:
            response = await self._command.RestoreAllMerchantPolicies(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_all(response)

    async def delete_all_permanent(self):
        try:
            response = await self._command.DeleteAllMerchantPoliciesPermanent(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_merchant_all(response)


__all__ = ["MerchantPolicyHandler", "normalize_pagination", "require_positive_id"]
