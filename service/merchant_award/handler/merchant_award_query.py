"""merchant_award query gRPC handler. `FindById` guards `id == 0` by returning `errors.ToGrpcError(errors.ErrInternal)` — a generic 500 "Internal server error", NOT a specific 400 (source has a `// Should use specific error if available` comment). reproduces. Every other failure is propagated from the service, which forwards the repository error unchanged (so a missing row stays 404)."""

from __future__ import annotations

from typing import Any

from pb.merchant_award import (
    merchant_award_common_pb2,
    merchant_award_query_pb2_grpc,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant_award.handler.mapping import (
    fill_merchant_award_response,
    fill_merchant_award_response_delete_at,
    normalize_page,
    pagination_meta,
)
from service.merchant_award.service.interfaces import MerchantAwardQueryService
from service.merchant_award.service.service import SERVICE_NAME
from shared.errors import err_internal


class MerchantAwardQueryHandler(
    merchant_award_query_pb2_grpc.MerchantAwardQueryServiceServicer
):
    def __init__(self, service: MerchantAwardQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantAwardQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_all(request.search, page, page_size)
        response = merchant_award_common_pb2.ApiResponsePaginationMerchantAward(
            status="success", message="Successfully fetched merchant"
        )
        for row in rows:
            fill_merchant_award_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("MerchantAwardQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            # returns errors.ToGrpcError(errors.ErrInternal) here, not a
            # dedicated invalid-id error (see module docstring).
            raise err_internal
        row = await self._service.find_by_id(request.id)
        response = merchant_award_common_pb2.ApiResponseMerchantAward(
            status="success", message="Successfully fetched merchant"
        )
        fill_merchant_award_response(response.data, row)
        return response

    @grpc_method("MerchantAwardQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_active(request.search, page, page_size)
        response = (
            merchant_award_common_pb2.ApiResponsePaginationMerchantAwardDeleteAt(
                status="success",
                message="Successfully fetched active merchant",
            )
        )
        for row in rows:
            fill_merchant_award_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("MerchantAwardQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_trashed(request.search, page, page_size)
        response = (
            merchant_award_common_pb2.ApiResponsePaginationMerchantAwardDeleteAt(
                status="success",
                message="Successfully fetched trashed merchant",
            )
        )
        for row in rows:
            fill_merchant_award_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response


__all__ = ["MerchantAwardQueryHandler"]
