"""Order item query gRPC handler. Pagination clamps match (page <= 0 -> 1, page_size <= 0 -> 10). Failures propagate as `AppError` and the `@grpc_method` decorator maps them exactly as `errors.ToGrpcError` does — the service already collapsed them to its own sentinels. `FindOrderItemByOrder` performs no id guard (reads the id and calls the service directly, so id=0 yields an empty list)."""

from __future__ import annotations

import math
from typing import Any

from pb.common import api_pb2 as common_pb2
from pb.order_item import order_item_common_pb2, order_item_query_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.order_item.handler.mapping import (
    fill_order_item_response,
    fill_order_item_response_delete_at,
)
from service.order_item.service.interfaces import OrderItemQueryService
from service.order_item.service.service import SERVICE_NAME


def _normalize(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def _total_pages(total: int, page_size: int) -> int:
    return math.ceil(total / page_size) if page_size else 0


def _pagination(page: int, page_size: int, total: int) -> Any:
    return common_pb2.PaginationMeta(
        current_page=page,
        page_size=page_size,
        total_pages=_total_pages(total, page_size),
        total_records=total,
    )


class OrderItemQueryHandler(
    order_item_query_pb2_grpc.OrderItemQueryServiceServicer
):
    def __init__(self, service: OrderItemQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("OrderItemQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        rows, total = await self._service.find_all(
            request.search, page, page_size
        )

        response = order_item_common_pb2.ApiResponsePaginationOrderItem(
            status="success", message="Successfully fetched order items"
        )
        for row in rows:
            fill_order_item_response(response.data.add(), row)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("OrderItemQueryService.FindByActive", SERVICE_NAME)
    async def FindByActive(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        rows, total = await self._service.find_active(
            request.search, page, page_size
        )

        response = order_item_common_pb2.ApiResponsePaginationOrderItemDeleteAt(
            status="success", message="Successfully fetched active order items"
        )
        for row in rows:
            fill_order_item_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("OrderItemQueryService.FindByTrashed", SERVICE_NAME)
    async def FindByTrashed(self, request: Any, context: Any) -> Any:
        page, page_size = _normalize(request.page, request.page_size)
        rows, total = await self._service.find_trashed(
            request.search, page, page_size
        )

        response = order_item_common_pb2.ApiResponsePaginationOrderItemDeleteAt(
            status="success", message="Successfully fetched trashed order items"
        )
        for row in rows:
            fill_order_item_response_delete_at(response.data.add(), row)
        response.pagination.CopyFrom(_pagination(page, page_size, total))
        return response

    @grpc_method("OrderItemQueryService.FindOrderItemByOrder", SERVICE_NAME)
    async def FindOrderItemByOrder(self, request: Any, context: Any) -> Any:
        rows = await self._service.find_by_order(int(request.id))

        response = order_item_common_pb2.ApiResponsesOrderItem(
            status="success", message="Successfully fetched order items by order"
        )
        for row in rows:
            fill_order_item_response(response.data.add(), row)
        return response


__all__ = ["OrderItemQueryHandler"]
