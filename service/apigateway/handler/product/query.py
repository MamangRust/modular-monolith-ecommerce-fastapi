"""Product query REST routes. Static paths (`/active`, `/trashed`) are registered before `/{product_id}` because Starlette matches routes in registration order (unlike Echo/chi, which prioritise static segments). Without this ordering `/active` would be captured as product_id="active". the gateway does not forward `min_price`/`max_price` on the merchant/category routes, so accepts only the shared paging/search params."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.product.handler import ProductHandler
from shared.domain.response.product import (
    ProductResponse,
    ProductResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination

router = APIRouter(prefix="/api/product-query", tags=["product-query"])


def get_product_handler(request: Request) -> ProductHandler:
    return ProductHandler(request.app.state.connections, request.app.state.upload_image)


@router.get("")
async def find_all_product(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ProductResponse]]:
    return await get_product_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_product(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ProductResponseDeleteAt]]:
    return await get_product_handler(request).find_by_active(page, page_size, search)


@router.get("/trashed")
async def find_trashed_product(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ProductResponseDeleteAt]]:
    return await get_product_handler(request).find_by_trashed(page, page_size, search)


@router.get("/merchant/{merchant_id}")
async def find_products_by_merchant(
    request: Request,
    merchant_id: int,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ProductResponse]]:
    return await get_product_handler(request).find_by_merchant(merchant_id, page, page_size, search)


@router.get("/category/{category_name}")
async def find_products_by_category(
    request: Request,
    category_name: str,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ProductResponse]]:
    return await get_product_handler(request).find_by_category(category_name, page, page_size, search)


@router.get("/{product_id}")
async def find_product_by_id(
    request: Request,
    product_id: int,
) -> ApiResponse[ProductResponse]:
    return await get_product_handler(request).find_by_id(product_id)


__all__ = ["router"]
