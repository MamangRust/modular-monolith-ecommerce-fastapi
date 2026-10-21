"""Banner query REST routes.

Static paths are registered before `/{banner_id}`: Starlette matches routes
in registration order (unlike chi, which prioritises static segments), so
`/active` would otherwise be captured as banner_id="active"."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.banner.handler import BannerHandler
from shared.domain.response.banner import (
    BannerResponse,
    BannerResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse, APIResponsePagination

router = APIRouter(prefix="/api/banner-query", tags=["banner-query"])


def get_banner_handler(request: Request) -> BannerHandler:
    return BannerHandler(request.app.state.connections)


@router.get("")
async def find_all_banner(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[BannerResponse]]:
    return await get_banner_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_banner(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[BannerResponseDeleteAt]]:
    return await get_banner_handler(request).find_by_active(page, page_size, search)


@router.get("/trashed")
async def find_trashed_banner(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[BannerResponseDeleteAt]]:
    return await get_banner_handler(request).find_by_trashed(page, page_size, search)


@router.get("/{banner_id}")
async def find_banner_by_id(
    request: Request,
    banner_id: int,
) -> ApiResponse[BannerResponse]:
    return await get_banner_handler(request).find_by_id(banner_id)


__all__ = ["router"]
