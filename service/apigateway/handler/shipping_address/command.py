"""Shipping address command REST routes. Static paths (`/restore/all`, `/permanent/all`) are registered before the `{id}` variants because Starlette matches in registration order — otherwise `/restore/all` would be captured as id="all". `Create`/`Update`/`DeleteByOrderPermanent` are internal gRPC used by the order service and are not exposed here (wires only the five routes below)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.shipping_address.handler import (
    ShippingAddressHandler,
)
from shared.domain.response.responses import ApiResponse
from shared.domain.response.shipping_address import ShippingAddressResponseDeleteAt

router = APIRouter(
    prefix="/api/shipping-address-command", tags=["shipping-address-command"]
)


def get_shipping_address_handler(request: Request) -> ShippingAddressHandler:
    return ShippingAddressHandler(request.app.state.connections)


@router.post("/trashed/{shipping_id}")
async def trash_shipping_address(
    request: Request,
    shipping_id: int,
) -> ApiResponse[ShippingAddressResponseDeleteAt]:
    return await get_shipping_address_handler(request).trash(shipping_id)


# Static paths first — `/restore/all` and `/permanent/all` must not be captured
# as id="all" by the dynamic routes below.
@router.post("/restore/all")
async def restore_all_shipping_address(request: Request) -> ApiResponse[None]:
    return await get_shipping_address_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_shipping_address_permanent(request: Request) -> ApiResponse[None]:
    return await get_shipping_address_handler(request).delete_all_permanent()


@router.post("/restore/{shipping_id}")
async def restore_shipping_address(
    request: Request,
    shipping_id: int,
) -> ApiResponse[ShippingAddressResponseDeleteAt]:
    return await get_shipping_address_handler(request).restore(shipping_id)


@router.delete("/permanent/{shipping_id}")
async def delete_shipping_address_permanent(
    request: Request,
    shipping_id: int,
) -> ApiResponse[None]:
    return await get_shipping_address_handler(request).delete_permanent(shipping_id)


__all__ = ["router"]
