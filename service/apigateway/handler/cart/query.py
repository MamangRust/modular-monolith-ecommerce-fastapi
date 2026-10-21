"""Cart query REST routes.

The owner id comes from the JWT subject (`request.state.user_id`, set by the
auth middleware); the handler rejects a missing subject with 401. The gateway
does not cache the listing."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.cart.handler import CartHandler
from shared.domain.response.cart import CartResponse
from shared.domain.response.responses import APIResponsePagination

router = APIRouter(prefix="/api/cart-query", tags=["cart-query"])


def get_cart_handler(request: Request) -> CartHandler:
    return CartHandler(request.app.state.connections)


@router.get("")
async def find_all_cart(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[CartResponse]]:
    return await get_cart_handler(request).find_all(
        getattr(request.state, "user_id", None), page, page_size, search
    )


__all__ = ["router"]
