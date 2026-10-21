"""order query gRPC handler. `FindAll`/`FindByActive`/`FindByTrashed` normalise paging and read the window `total` from the service. `FindById` guards `id == 0` with the order-specific `err_grpc_order_invalid_id` (400 "Invalid ID"). The proto `FindAllOrderMerchantRequest`/`FindByMerchant` RPC is not part of `OrderQueryService` (query handler has no `FindByMerchant` method), so the service's `find_by_merchant` is not served here."""

from __future__ import annotations

from typing import Any

from pb.order import order_common_pb2, order_query_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.order.handler.mapping import (
    fill_order_response,
    fill_order_response_delete_at,
    normalize_page,
    pagination_meta,
)
from service.order.service.interfaces import OrderQueryService
from service.order.service.service import SERVICE_NAME
from shared.domain.requests.order import FindAllOrder
from shared.errors.order_errors import err_grpc_order_invalid_id


class OrderQueryHandler(order_query_pb2_grpc.OrderQueryServiceServicer):
    def __init__(self, service: OrderQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("OrderQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_all(
            FindAllOrder(search=request.search, page=page, page_size=page_size)
        )
        response = order_common_pb2.ApiResponsePaginationOrder(
            status="success", message="Successfully fetched order"
        )
        for row in rows:
            fill_order_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("OrderQueryService.FindById", SERVICE_NAME)
    async def FindById(self, request: Any, context: Any) -> Any:
        if request.id == 0:
            raise err_grpc_order_invalid_id
        row = await self._service.find_by_id(int(request.id))
        response = order_common_pb2.ApiResponseOrder(
            status="success", message="Successfully fetched order"
        )
        fill_order_response(response.data, row)
        return response

    @grpc_method("OrderQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_active(
            FindAllOrder(search=request.search, page=page, page_size=page_size)
        )
        response = order_common_pb2.ApiResponsePaginationOrderDeleteAt(
            status="success", message="Successfully fetched active order"
        )
        for row in rows:
            fill_order_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response

    @grpc_method("OrderQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_trashed(
            FindAllOrder(search=request.search, page=page, page_size=page_size)
        )
        response = order_common_pb2.ApiResponsePaginationOrderDeleteAt(
            status="success", message="Successfully fetched trashed order"
        )
        for row in rows:
            fill_order_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response


__all__ = ["OrderQueryHandler"]
