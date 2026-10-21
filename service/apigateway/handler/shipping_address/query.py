"""Shipping address query REST routes.

Registered on a flat `/api/shipping-address-query` prefix. Static segments
precede any dynamic one, because Starlette matches routes in registration
order (unlike chi, which prioritises static segments) — otherwise `/active`
and `/trashed` would be captured as `id="active"`/`id="trashed"`."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.shipping_address.handler import (
    ShippingAddressHandler,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.domain.response.shipping_address import (
    ShippingAddressResponse,
    ShippingAddressResponseDeleteAt,
)

router = APIRouter(
    prefix="/api/shipping-address-query", tags=["shipping-address-query"]
)


def get_shipping_address_handler(request: Request) -> ShippingAddressHandler:
    return ShippingAddressHandler(request.app.state.connections)


@router.get("")
async def find_all_shipping_address(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ShippingAddressResponse]]:
    return await get_shipping_address_handler(request).find_all(
        page, page_size, search
    )


# Static paths first — `/active` and `/trashed` must not be captured as
# id="active"/id="trashed" by the dynamic route below.
@router.get("/active")
async def find_active_shipping_address(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ShippingAddressResponseDeleteAt]]:
    return await get_shipping_address_handler(request).find_by_active(
        page, page_size, search
    )


@router.get("/trashed")
async def find_trashed_shipping_address(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ShippingAddressResponseDeleteAt]]:
    return await get_shipping_address_handler(request).find_by_trashed(
        page, page_size, search
    )


@router.get("/order/{order_id}")
async def find_shipping_address_by_order(
    request: Request,
    order_id: int,
) -> ApiResponse[ShippingAddressResponse]:
    return await get_shipping_address_handler(request).find_by_order(order_id)


@router.get("/{shipping_id}")
async def find_shipping_address_by_id(
    request: Request,
    shipping_id: int,
) -> ApiResponse[ShippingAddressResponse]:
    return await get_shipping_address_handler(request).find_by_id(shipping_id)


__all__ = ["router"]
