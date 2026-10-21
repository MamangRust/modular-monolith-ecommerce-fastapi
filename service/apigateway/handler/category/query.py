"""Category query REST routes.

Static paths are registered before `/{category_id}`: Starlette matches routes
in registration order (unlike chi, which prioritises static segments), so
`/active` would otherwise be captured as category_id="active"."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.category.handler import CategoryHandler
from shared.domain.response.category import (
    CategoryResponse,
    CategoryResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination

router = APIRouter(prefix="/api/category-query", tags=["category-query"])


def get_category_handler(request: Request) -> CategoryHandler:
    return CategoryHandler(
        request.app.state.connections, request.app.state.upload_image
    )


@router.get("")
async def find_all_category(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[CategoryResponse]]:
    return await get_category_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_category(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[CategoryResponseDeleteAt]]:
    return await get_category_handler(request).find_by_active(page, page_size, search)


@router.get("/trashed")
async def find_trashed_category(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[CategoryResponseDeleteAt]]:
    return await get_category_handler(request).find_by_trashed(page, page_size, search)


@router.get("/{category_id}")
async def find_category_by_id(
    request: Request,
    category_id: int,
) -> ApiResponse[CategoryResponse]:
    return await get_category_handler(request).find_by_id(category_id)


__all__ = ["router"]
