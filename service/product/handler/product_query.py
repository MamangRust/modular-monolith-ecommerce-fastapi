"""product query gRPC handler. `FindAll`/`FindByMerchant`/`FindByCategory`/`FindByActive`/`FindByTrashed` normalise paging via `normalize_page` and read the window `total` from the service. `FindById` has no `id == 0` guard — the query handler never references its `err_grpc_*` sentinels, so a 0 id simply reaches the repository and answers 404."""

from __future__ import annotations

from typing import Any

from pb.product import product_common_pb2, product_query_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.product.handler.mapping import (
    fill_product_response,
    fill_product_response_delete_at,
    normalize_page,
    pagination_meta,
)
from service.product.service.interfaces import ProductQueryService
from service.product.service.service import SERVICE_NAME


class ProductQueryHandler(product_query_pb2_grpc.ProductQueryServiceServicer):
    def __init__(self, service: ProductQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("ProductQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_all(request.search, page, page_size)
        response = product_common_pb2.ApiResponsePaginationProduct(
            status="success", message="Successfully fetched products"
        )
        for row in rows:
            fill_product_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("ProductQueryService.FindByMerchant", SERVICE_NAME)
    async def FindByMerchant(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_by_merchant(
            request.merchant_id,
            request.category_id,
            request.search,
            request.min_price,
            request.max_price,
            page,
            page_size,
        )
        response = product_common_pb2.ApiResponsePaginationProduct(
            status="success", message="Successfully fetched merchant products"
        )
        for row in rows:
            fill_product_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("ProductQueryService.FindByCategory", SERVICE_NAME)
    async def FindByCategory(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_by_category(
            request.category_name,
            request.search,
            request.min_price,
            request.max_price,
            page,
            page_size,
        )
        response = product_common_pb2.ApiResponsePaginationProduct(
            status="success", message="Successfully fetched category products"
        )
        for row in rows:
            fill_product_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("ProductQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        row = await self._service.find_by_id(request.id)
        response = product_common_pb2.ApiResponseProduct(
            status="success", message="Successfully fetched product"
        )
        fill_product_response(response.data, row)
        return response

    @grpc_method("ProductQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_active(request.search, page, page_size)
        response = product_common_pb2.ApiResponsePaginationProductDeleteAt(
            status="success", message="Successfully fetched active products"
        )
        for row in rows:
            fill_product_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("ProductQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_trashed(request.search, page, page_size)
        response = product_common_pb2.ApiResponsePaginationProductDeleteAt(
            status="success", message="Successfully fetched trashed products"
        )
        for row in rows:
            fill_product_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response


__all__ = ["ProductQueryHandler"]
