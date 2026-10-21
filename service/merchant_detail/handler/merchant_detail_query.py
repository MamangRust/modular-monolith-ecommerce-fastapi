"""merchant_detail query gRPC handler.

`FindById` guards `id == 0` with `err_grpc_invalid_merchant_detail_id` (400).
Every other failure is propagated from the service and mapped to its original
code by the `grpc_method` decorator (the service remaps most reads to its own
sentinels — see the service module)."""

from __future__ import annotations

from typing import Any

from pb.merchant_detail import (
    merchant_detail_common_pb2,
    merchant_detail_query_pb2_grpc,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant_detail.handler.mapping import (
    fill_merchant_detail_response,
    fill_merchant_detail_response_delete_at,
    normalize_page,
    pagination_meta,
)
from service.merchant_detail.service.interfaces import (
    MerchantDetailQueryService,
)
from service.merchant_detail.service.service import SERVICE_NAME
from shared.errors.merchant_detail_errors import (
    err_grpc_invalid_merchant_detail_id,
)


class MerchantDetailQueryHandler(
    merchant_detail_query_pb2_grpc.MerchantDetailQueryServiceServicer
):
    def __init__(self, service: MerchantDetailQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantDetailQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_all(request.search, page, page_size)
        response = merchant_detail_common_pb2.ApiResponsePaginationMerchantDetail(
            status="success", message="Successfully fetched merchant details"
        )
        for row in rows:
            fill_merchant_detail_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("MerchantDetailQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_detail_id
        row = await self._service.find_by_id(request.id)
        response = merchant_detail_common_pb2.ApiResponseMerchantDetail(
            status="success", message="Successfully fetched merchant detail"
        )
        fill_merchant_detail_response(response.data, row)
        return response

    @grpc_method("MerchantDetailQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_active(request.search, page, page_size)
        response = (
            merchant_detail_common_pb2.ApiResponsePaginationMerchantDetailDeleteAt(
                status="success",
                message="Successfully fetched active merchant details",
            )
        )
        for row in rows:
            fill_merchant_detail_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("MerchantDetailQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_trashed(
            request.search, page, page_size
        )
        response = (
            merchant_detail_common_pb2.ApiResponsePaginationMerchantDetailDeleteAt(
                status="success",
                message="Successfully fetched trashed merchant details",
            )
        )
        for row in rows:
            fill_merchant_detail_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response


__all__ = ["MerchantDetailQueryHandler"]
