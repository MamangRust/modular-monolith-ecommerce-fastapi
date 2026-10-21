"""merchant_business query gRPC handler."""

from __future__ import annotations

from typing import Any

from pb.merchant_business import (
    merchant_business_common_pb2,
    merchant_business_query_pb2_grpc,
)
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant_business.handler.mapping import (
    fill_merchant_business_response,
    fill_merchant_business_response_delete_at,
    normalize_page,
    pagination_meta,
)
from service.merchant_business.service.interfaces import (
    MerchantBusinessQueryService,
)
from service.merchant_business.service.service import SERVICE_NAME
from shared.errors import err_grpc_invalid_merchant_business_id


class MerchantBusinessQueryHandler(
    merchant_business_query_pb2_grpc.MerchantBusinessQueryServiceServicer
):
    def __init__(self, service: MerchantBusinessQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantBusinessQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_all(request.search, page, page_size)
        response = merchant_business_common_pb2.ApiResponsePaginationMerchantBusiness(
            status="success", message="Successfully fetched merchant"
        )
        for row in rows:
            fill_merchant_business_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("MerchantBusinessQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_business_id
        row = await self._service.find_by_id(request.id)
        response = merchant_business_common_pb2.ApiResponseMerchantBusiness(
            status="success", message="Successfully fetched merchant"
        )
        fill_merchant_business_response(response.data, row)
        return response

    @grpc_method("MerchantBusinessQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_active(request.search, page, page_size)
        response = (
            merchant_business_common_pb2.ApiResponsePaginationMerchantBusinessDeleteAt(
                status="success",
                message="Successfully fetched active merchant",
            )
        )
        for row in rows:
            fill_merchant_business_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("MerchantBusinessQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_trashed(request.search, page, page_size)
        response = (
            merchant_business_common_pb2.ApiResponsePaginationMerchantBusinessDeleteAt(
                status="success",
                message="Successfully fetched trashed merchant",
            )
        )
        for row in rows:
            fill_merchant_business_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response


__all__ = ["MerchantBusinessQueryHandler"]
