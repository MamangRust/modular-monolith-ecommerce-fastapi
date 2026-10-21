"""Gateway cart handler: REST <-> cart gRPC. Only transport concerns live here: build the proto request, call the domain over gRPC, convert a gRPC failure back to its original AppError, and map the proto response to the shared response envelope. No SQL, no business rules. Like the other domains, deliberately does not cache in the gateway. gateway cart handler caches under its own `cart:all:` namespace and invalidates on every mutation; drops that layer, so every request goes straight to the cart service, which serves/invalidates its own `cart:svc:` cache. The owner id always comes from the JWT (`request.state.user_id`, set by the auth middleware) and never from the body — the route passes it in and a missing subject is a 401 (`err_unauthorized`), matching `user_id` context check."""

from __future__ import annotations

import grpc

from pb.cart import cart_command_pb2, cart_command_pb2_grpc, cart_query_pb2, cart_query_pb2_grpc
from service.apigateway.app.client import ServiceConnections
from shared.domain.response.cart import CartResponse
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.errors import err_unauthorized, parse_grpc_error
from shared.mapper.cart import (
    to_api_response_cart,
    to_api_response_cart_all,
    to_api_response_cart_delete,
    to_api_response_pagination_cart,
)

RPC_TIMEOUT = 30.0


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Gateway-side clamping."""
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class CartHandler:
    def __init__(self, connections: ServiceConnections) -> None:
        channel = connections.channel("cart")
        self._query = cart_query_pb2_grpc.CartQueryServiceStub(channel)
        self._command = cart_command_pb2_grpc.CartCommandServiceStub(channel)

    # ---- query ----

    async def find_all(
        self, user_id: int | None, page: int, page_size: int, search: str
    ) -> APIResponsePagination[list[CartResponse]]:
        if not user_id or user_id <= 0:
            raise err_unauthorized
        page, page_size = normalize_pagination(page, page_size)
        request = cart_query_pb2.FindAllCartRequest(
            user_id=user_id,
            page=page,
            page_size=page_size,
            search=search or "",
        )
        try:
            response = await self._query.FindAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_pagination_cart(response)

    # ---- command ----

    async def create(
        self, user_id: int | None, product_id: int, quantity: int
    ) -> ApiResponse[CartResponse]:
        if not user_id or user_id <= 0:
            raise err_unauthorized
        request = cart_command_pb2.CreateCartRequest(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )
        try:
            response = await self._command.Create(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_cart(response)

    async def delete(self, user_id: int | None, cart_id: int) -> ApiResponse[None]:
        if not user_id or user_id <= 0:
            raise err_unauthorized
        request = cart_command_pb2.DeleteCartRequest(user_id=user_id, cart_id=cart_id)
        try:
            response = await self._command.Delete(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_cart_delete(response)

    async def delete_all(
        self, user_id: int | None, cart_ids: list[int]
    ) -> ApiResponse[None]:
        if not user_id or user_id <= 0:
            raise err_unauthorized
        request = cart_command_pb2.DeleteAllCartRequest(
            user_id=user_id,
            cart_ids=list(cart_ids),
        )
        try:
            response = await self._command.DeleteAll(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_api_response_cart_all(response)


__all__ = ["CartHandler", "normalize_pagination"]
