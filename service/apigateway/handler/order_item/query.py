"""Order item query REST routes.

Registered on a flat `/api/order-item` prefix. Static segments precede any
dynamic one, because Starlette matches routes in registration order (unlike
chi, which prioritises static segments)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.order_item.handler import OrderItemHandler
from shared.domain.response.order_item import (
    OrderItemResponse,
    OrderItemResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination

router = APIRouter(prefix="/api/order-item", tags=["order-item-query"])


def get_order_item_handler(request: Request) -> OrderItemHandler:
    return OrderItemHandler(request.app.state.connections)


@router.get("")
async def find_all_order_item(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[OrderItemResponse]]:
    return await get_order_item_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_order_item(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[OrderItemResponseDeleteAt]]:
    return await get_order_item_handler(request).find_by_active(
        page, page_size, search
    )


@router.get("/trashed")
async def find_trashed_order_item(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[OrderItemResponseDeleteAt]]:
    return await get_order_item_handler(request).find_by_trashed(
        page, page_size, search
    )


@router.get("/order/{order_id}")
async def find_order_item_by_order(
    request: Request,
    order_id: int,
) -> ApiResponse[list[OrderItemResponse]]:
    return await get_order_item_handler(request).find_by_order(order_id)


__all__ = ["router"]
