"""cart query gRPC handler.

`FindAll` normalises paging via `normalize_page`, reads the window `total` from
the service, and formats the timestamps date-only. The query service exposes only
`FindAll` (the `FindByIdCartRequest` message exists in the proto but no RPC uses
it), so that is the sole method."""

from __future__ import annotations

from typing import Any

from pb.cart import cart_common_pb2, cart_query_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.cart.handler.mapping import (
    fill_cart_response,
    normalize_page,
    pagination_meta,
)
from service.cart.service.interfaces import CartQueryService
from service.cart.service.service import SERVICE_NAME
from shared.domain.requests.cart import FindAllCarts


class CartQueryHandler(cart_query_pb2_grpc.CartQueryServiceServicer):
    def __init__(self, service: CartQueryService, logger: Logger) -> None:
        self._service = service
        self.logger = logger

    @grpc_method("CartQueryService.FindAll", SERVICE_NAME)
    async def FindAll(self, request: Any, context: Any) -> Any:
        page, page_size = normalize_page(request.page, request.page_size)
        rows, total = await self._service.find_all(
            FindAllCarts(
                user_id=request.user_id,
                page=page,
                page_size=page_size,
                search=request.search,
            )
        )
        response = cart_common_pb2.ApiResponsePaginationCart(
            status="success", message="Successfully fetched cart items"
        )
        for row in rows:
            fill_cart_response(response.data.add(), row)
        response.pagination.CopyFrom(pagination_meta(page, page_size, total))
        return response


__all__ = ["CartQueryHandler"]
