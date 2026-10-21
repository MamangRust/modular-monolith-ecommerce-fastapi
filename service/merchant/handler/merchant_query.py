"""Merchant query gRPC handler.

`FindById` guards `id == 0` with `err_grpc_invalid_merchant_id` (400). Every
other failure is propagated from the service and mapped to its original code by
the `grpc_method` decorator (a repository 404 stays `NOT_FOUND`)."""

from __future__ import annotations

from typing import Any

from pb.merchant import merchant_common_pb2, merchant_query_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.merchant.handler.mapping import (
    fill_merchant_response,
    fill_merchant_response_delete_at,
    normalize_page,
    pagination_meta,
)
from service.merchant.service.interfaces import MerchantQueryService
from service.merchant.service.service import SERVICE_NAME
from shared.errors.merchant_errors import err_grpc_invalid_merchant_id


class MerchantQueryHandler(merchant_query_pb2_grpc.MerchantQueryServiceServicer):
    def __init__(self, service: MerchantQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("MerchantQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_all(request.search, page, page_size)
        response = merchant_common_pb2.ApiResponsePaginationMerchant(
            status="success", message="Successfully fetched merchants"
        )
        for row in rows:
            fill_merchant_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("MerchantQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_invalid_merchant_id
        merchant = await self._service.find_by_id(request.id)
        response = merchant_common_pb2.ApiResponseMerchant(
            status="success", message="Successfully fetched merchant"
        )
        fill_merchant_response(response.data, merchant)
        return response

    @grpc_method("MerchantQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_active(request.search, page, page_size)
        response = merchant_common_pb2.ApiResponsePaginationMerchantDeleteAt(
            status="success", message="Successfully fetched active merchants"
        )
        for row in rows:
            fill_merchant_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("MerchantQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_trashed(request.search, page, page_size)
        response = merchant_common_pb2.ApiResponsePaginationMerchantDeleteAt(
            status="success", message="Successfully fetched trashed merchants"
        )
        for row in rows:
            fill_merchant_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response


__all__ = ["MerchantQueryHandler"]
