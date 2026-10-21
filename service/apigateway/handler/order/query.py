"""Order query REST routes. registers `/:id` before `/active` and `/trashed`; Echo prioritises static segments so the latter still match. Starlette matches routes in registration order, so registers the static `/active` and `/trashed` first and the `/{order_id}` route last (otherwise `/active` would be captured as an id). The gateway does not cache."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.order.handler import OrderHandler
from shared.domain.response.order import (
    OrderResponseApi,
    OrderResponsePagination,
    OrderResponsePaginationDeleteAt,
)

router = APIRouter(prefix="/api/order-query", tags=["order-query"])


def get_order_handler(request: Request) -> OrderHandler:
    return OrderHandler(request.app.state.connections)


@router.get("")
async def find_all_order(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> OrderResponsePagination:
    return await get_order_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_order(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> OrderResponsePaginationDeleteAt:
    return await get_order_handler(request).find_by_active(page, page_size, search)


@router.get("/trashed")
async def find_trashed_order(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> OrderResponsePaginationDeleteAt:
    return await get_order_handler(request).find_by_trashed(page, page_size, search)


# Registered last: Starlette matches in order, so a literal `/active` or
# `/trashed` must be reachable before this capture-all id route.
@router.get("/{order_id}")
async def find_order_by_id(
    request: Request,
    order_id: int,
) -> OrderResponseApi:
    return await get_order_handler(request).find_by_id(order_id)


__all__ = ["router"]
