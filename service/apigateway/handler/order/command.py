"""Order command REST routes. binds and validates the JSON body (`CreateOrderRequest`/`UpdateOrderRequest`); reuses the shared pydantic DTOs, so an invalid body yields the global 400 `"Validation failed"` envelope rather than FastAPI's 422. The whole order command surface returns **200** (uses `http.StatusOK` everywhere, unlike review's create which is 201), and the gateway does not cache. `Create` takes `merchant_id`/`user_id` from the **body** (the order gateway never reads the JWT subject). `Update` uses the path id and ignores the body's `order_id`. registers `/restore/all` and `/permanent/all` after their `/:id` variants but Echo prioritises static segments; Starlette matches in registration order, so the static paths first."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.order.handler import OrderHandler
from shared.domain.requests.order import (
    CreateOrderRequest,
    UpdateOrderRequest,
)
from shared.domain.response.order import (
    OrderResponseAll,
    OrderResponseApi,
    OrderResponseDelete,
    OrderResponseDeleteAtApi,
)

router = APIRouter(prefix="/api/order-command", tags=["order-command"])


def get_order_handler(request: Request) -> OrderHandler:
    return OrderHandler(request.app.state.connections)


@router.post("/create")
async def create_order(
    request: Request,
    body: CreateOrderRequest,
) -> OrderResponseApi:
    return await get_order_handler(request).create(body)


# Static paths first — `/restore/all` must not be captured as order_id="all".
@router.post("/restore/all")
async def restore_all_order(request: Request) -> OrderResponseAll:
    return await get_order_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_order_permanent(request: Request) -> OrderResponseAll:
    return await get_order_handler(request).delete_all_permanent()


@router.post("/update/{order_id}")
async def update_order(
    request: Request,
    order_id: int,
    body: UpdateOrderRequest,
) -> OrderResponseApi:
    return await get_order_handler(request).update(order_id, body)


@router.post("/trashed/{order_id}")
async def trash_order(
    request: Request,
    order_id: int,
) -> OrderResponseDeleteAtApi:
    return await get_order_handler(request).trash(order_id)


@router.post("/restore/{order_id}")
async def restore_order(
    request: Request,
    order_id: int,
) -> OrderResponseDeleteAtApi:
    return await get_order_handler(request).restore(order_id)


@router.delete("/permanent/{order_id}")
async def delete_order_permanent(
    request: Request,
    order_id: int,
) -> OrderResponseDelete:
    return await get_order_handler(request).delete_permanent(order_id)


__all__ = ["router"]
