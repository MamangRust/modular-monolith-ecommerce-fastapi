"""Gateway shipping address handler: REST <-> shipping_address gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. Like the gateway (and banner/order_item), a non-positive path id is rejected before the gRPC hop with a 400 `"Invalid ID"` — uses that same message for both the by-id and by-order routes here. the gateway's per-domain Redis cache is not (same deviation as banner/category): caching stays inside the domain service. `Create`/`Update`/`DeleteByOrderPermanent` are internal gRPC used by the order service and are intentionally not exposed as REST routes, wires them."""

from __future__ import annotations

import grpc
from google.protobuf import empty_pb2

from pb.shipping_address import (
    shipping_address_command_pb2_grpc,
    shipping_address_common_pb2,
    shipping_address_query_pb2,
    shipping_address_query_pb2_grpc,
)
from service.apigateway.app.client import ServiceConnections
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.domain.response.shipping_address import (
    ShippingAddressResponse,
    ShippingAddressResponseDeleteAt,
)
from shared.errors import new_bad_request_error, parse_grpc_error
from shared.mapper.shipping_address import (
    to_api_response_pagination_shipping_address,
    to_api_response_pagination_shipping_address_delete_at,
    to_api_response_shipping_address,
    to_api_response_shipping_address_all,
    to_api_response_shipping_address_delete,
    to_api_response_shipping_address_delete_at,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


def require_positive_id(shipping_id: int) -> None:
    """Reject a non-positive path id before the gRPC hop (`"Invalid ID"`)."""
    if shipping_id <= 0:
        raise new_bad_request_error("Invalid ID")


class ShippingAddressHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("shipping_address")
        self._query = shipping_address_query_pb2_grpc.ShippingQueryServiceStub(channel)
        self._command = shipping_address_command_pb2_grpc.ShippingCommandServiceStub(
            channel
        )

    # ---- query ----

    async def find_all(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ShippingAddressResponse]]:
        page, page_size = normalize_pagination(page, page_size)
        request = shipping_address_query_pb2.FindAllShippingRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_shipping_address(response)

    async def find_by_id(
        self, shipping_id: int
    ) -> ApiResponse[ShippingAddressResponse]:
        require_positive_id(shipping_id)
        request = shipping_address_common_pb2.FindByIdShippingRequest(id=shipping_id)
        try:
            response = await self._query.FindById(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_shipping_address(response)

    async def find_by_order(
        self, order_id: int
    ) -> ApiResponse[ShippingAddressResponse]:
        require_positive_id(order_id)
        request = shipping_address_common_pb2.FindByIdShippingRequest(id=order_id)
        try:
            response = await self._query.FindByOrder(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_shipping_address(response)

    async def find_by_active(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ShippingAddressResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = shipping_address_query_pb2.FindAllShippingRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByActive(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_shipping_address_delete_at(response)

    async def find_by_trashed(
        self, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[ShippingAddressResponseDeleteAt]]:
        page, page_size = normalize_pagination(page, page_size)
        request = shipping_address_query_pb2.FindAllShippingRequest(
            page=page, page_size=page_size, search=search or ""
        )
        try:
            response = await self._query.FindByTrashed(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_shipping_address_delete_at(response)

    # ---- command ----

    async def trash(
        self, shipping_id: int
    ) -> ApiResponse[ShippingAddressResponseDeleteAt]:
        require_positive_id(shipping_id)
        request = shipping_address_common_pb2.FindByIdShippingRequest(id=shipping_id)
        try:
            response = await self._command.TrashedShipping(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_shipping_address_delete_at(response)

    async def restore(
        self, shipping_id: int
    ) -> ApiResponse[ShippingAddressResponseDeleteAt]:
        require_positive_id(shipping_id)
        request = shipping_address_common_pb2.FindByIdShippingRequest(id=shipping_id)
        try:
            response = await self._command.RestoreShipping(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_shipping_address_delete_at(response)

    async def delete_permanent(self, shipping_id: int) -> ApiResponse[None]:
        require_positive_id(shipping_id)
        request = shipping_address_common_pb2.FindByIdShippingRequest(id=shipping_id)
        try:
            response = await self._command.DeleteShippingPermanent(
                request, timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_shipping_address_delete(response)

    async def restore_all(self) -> ApiResponse[None]:
        try:
            response = await self._command.RestoreAllShipping(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_shipping_address_all(response)

    async def delete_all_permanent(self) -> ApiResponse[None]:
        try:
            response = await self._command.DeleteAllShippingPermanent(
                empty_pb2.Empty(), timeout=RPC_TIMEOUT
            )
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_shipping_address_all(response)


__all__ = [
    "ShippingAddressHandler",
    "normalize_pagination",
    "require_positive_id",
]
