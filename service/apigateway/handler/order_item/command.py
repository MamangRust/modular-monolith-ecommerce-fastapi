"""Order item command REST routes. Static paths (`/restore/all`, `/permanent/all`) are registered before the `{id}` variants because Starlette matches in registration order — otherwise `/restore/all` would be captured as `id="all"`. `Create`/`Update`/`DeleteByOrderPermanent`/`CalculateTotalPrice` are internal gRPC used by the order service and are not exposed here (wires only the five routes below)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.order_item.handler import OrderItemHandler
from shared.domain.response.order_item import OrderItemResponse
from shared.domain.response.responses import ApiResponse

router = APIRouter(prefix="/api/order-item", tags=["order-item-command"])


def get_order_item_handler(request: Request) -> OrderItemHandler:
    return OrderItemHandler(request.app.state.connections)


@router.post("/trash/{order_item_id}")
async def trash_order_item(
    request: Request,
    order_item_id: int,
) -> ApiResponse[OrderItemResponse]:
    return await get_order_item_handler(request).trash(order_item_id)


# Static paths first — `/restore/all` and `/permanent/all` must not be captured
# as id="all" by the dynamic routes below.
@router.post("/restore/all")
async def restore_all_order_item(request: Request) -> ApiResponse[None]:
    return await get_order_item_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_order_item_permanent(request: Request) -> ApiResponse[None]:
    return await get_order_item_handler(request).delete_all_permanent()


@router.post("/restore/{order_item_id}")
async def restore_order_item(
    request: Request,
    order_item_id: int,
) -> ApiResponse[OrderItemResponse]:
    return await get_order_item_handler(request).restore(order_item_id)


@router.delete("/permanent/{order_item_id}")
async def delete_order_item_permanent(
    request: Request,
    order_item_id: int,
) -> ApiResponse[None]:
    return await get_order_item_handler(request).delete_permanent(order_item_id)


__all__ = ["router"]
