"""Gateway order item handler: REST <-> order_item gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. Like the gateway (and banner), a non-positive path id is rejected before the gRPC hop with a 400 — `"Invalid Order ID"` for the by-order lookup and `"Invalid ID"` for the command routes. the gateway's per-domain Redis cache is not (same deviation as banner/category): caching stays inside the domain service. `Create`/`Update`/`DeleteByOrderPermanent`/`CalculateTotalPrice` are internal gRPC used by the order service and are intentionally not exposed as REST routes, wires them."""

from __future__ import annotations

import grpc
from google.protobuf import empty_pb2

from pb.order_item import (
    order_item_command_pb2_grpc,
    order_item_common_pb2,
    order_item_query_pb2,
    order_item_query_pb2_grpc,
)
from service.apigateway.app.client import ServiceConnections
from shared.domain.response.order_item import (
    OrderItemResponse,
    OrderItemResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.errors import new_bad_request_error, parse_grpc_error
from shared.mapper.order_item import (
    to_api_response_order_item,
    to_api_response_order_item_all,
    to_api_response_order_item_delete,
    to_api_response_pagination_order_item,
    to_api_response_pagination_order_item_delete_at,
    to_api_responses_order_item,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def require_positive_id(order_item_id: int) -> None:
    """Reject a non-positive path id before the gRPC hop (`"Invalid ID"`)."""
    if order_item_id <= 0:
        raise new_bad_request_error("Invalid ID")


def require_positive_order_id(order_id: int) -> None:
    """Reject a non-positive order id before the gRPC hop."""
    if order_id <= 0:
        raise new_bad_request_error("Invalid Order ID")


class OrderItemHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("order_item")
        self._query = order_item_query_pb2_grpc.OrderItemQueryServiceStub(channel)
        self._command = order_item_command_pb2_grpc.OrderItemCommandServiceStub(channel)

    # ---- query ----

    async def find_all(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[OrderItemResponse]]:
        page, page_size = normalize_pagination(page, page_size)
        request = order_item_query_pb2.FindAllOrderItemRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_order_item(response)

    async def find_by_active(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[OrderItemResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = order_item_query_pb2.FindAllOrderItemRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_order_item_delete_at(response)

    async def find_by_trashed(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[OrderItemResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = order_item_query_pb2.FindAllOrderItemRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_order_item_delete_at(response)

    async def find_by_order(
        self, order_id: int
    ) -> ApiResponse[list[OrderItemResponse]]:
        require_positive_order_id(order_id)
        request = order_item_common_pb2.FindByIdOrderItemRequest(id=order_id)
        try:
            response = await self._query.FindOrderItemByOrder(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_responses_order_item(response)

    # ---- command ----

    async def trash(self, order_item_id: int) -> ApiResponse[OrderItemResponse]:
        require_positive_id(order_item_id)
        request = order_item_common_pb2.FindByIdOrderItemRequest(id=order_item_id)
        try:
            response = await self._command.TrashOrderItem(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order_item(response)

    async def restore(self, order_item_id: int) -> ApiResponse[OrderItemResponse]:
        require_positive_id(order_item_id)
        request = order_item_common_pb2.FindByIdOrderItemRequest(id=order_item_id)
        try:
            response = await self._command.RestoreOrderItem(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order_item(response)

    async def delete_permanent(self, order_item_id: int) -> ApiResponse[None]:
        require_positive_id(order_item_id)
        request = order_item_common_pb2.FindByIdOrderItemRequest(id=order_item_id)
        try:
            response = await self._command.DeleteOrderItemPermanent(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order_item_delete(response)

    async def restore_all(self) -> ApiResponse[None]:
        try:
            response = await self._command.RestoreAllOrdersItem(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order_item_all(response)

    async def delete_all_permanent(self) -> ApiResponse[None]:
        try:
            response = await self._command.DeleteAllPermanentOrdersItem(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_order_item_all(response)


__all__ = [
    "OrderItemHandler",
    "normalize_pagination",
    "require_positive_id",
    "require_positive_order_id",
]
