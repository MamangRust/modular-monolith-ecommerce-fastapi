"""merchant_policy query gRPC handler. `FindById` guards `id == 0` with `err_grpc_invalid_merchant_policy_id` — a 400 "invalid merchant policy id" (normalisation: the handler has no id guards at all and never references its `err_grpc_*` sentinels; wires them for with merchant_award/merchant_business). Every other failure is propagated from the service, which remaps reads to its own sentinels."""

from __future__ import annotations

from typing import Any

from pb.merchant_policy import (
    merchant_policy_common_pb2,
    merchant_policy_query_pb2_grpc,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant_policy.handler.mapping import (
    fill_merchant_policy_response,
    fill_merchant_policy_response_delete_at,
    normalize_page,
    pagination_meta,
)
from service.merchant_policy.service.interfaces import MerchantPolicyQueryService
from service.merchant_policy.service.service import SERVICE_NAME
from shared.errors import err_grpc_invalid_merchant_policy_id


class MerchantPolicyQueryHandler(
    merchant_policy_query_pb2_grpc.MerchantPolicyQueryServiceServicer
):
    def __init__(self, service: MerchantPolicyQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantPolicyQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_all(request.search, page, page_size)
        response = (
            merchant_policy_common_pb2.ApiResponsePaginationMerchantPolicies(
                status="success", message="Successfully fetched merchant policies"
            )
        )
        for row in rows:
            fill_merchant_policy_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("MerchantPolicyQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_policy_id
        row = await self._service.find_by_id(request.id)
        response = merchant_policy_common_pb2.ApiResponseMerchantPolicies(
            status="success", message="Successfully fetched merchant policy"
        )
        fill_merchant_policy_response(response.data, row)
        return response

    @grpc_method("MerchantPolicyQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_active(request.search, page, page_size)
        response = (
            merchant_policy_common_pb2.ApiResponsePaginationMerchantPoliciesDeleteAt(
                status="success",
                message="Successfully fetched merchant policies",
            )
        )
        for row in rows:
            fill_merchant_policy_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("MerchantPolicyQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_trashed(request.search, page, page_size)
        response = (
            merchant_policy_common_pb2.ApiResponsePaginationMerchantPoliciesDeleteAt(
                status="success",
                message="Successfully fetched merchant policies",
            )
        )
        for row in rows:
            fill_merchant_policy_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response


__all__ = ["MerchantPolicyQueryHandler"]
