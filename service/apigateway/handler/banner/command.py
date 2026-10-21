"""Banner command REST routes.

Static paths (`/restore/all`, `/permanent/all`) are registered before the
`{banner_id}` variants because Starlette matches in registration order."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.banner.handler import BannerHandler
from shared.domain.requests.banner import CreateBannerRequest, UpdateBannerRequest
from shared.domain.response.banner import (
    BannerResponse,
    BannerResponseDeleteAt,
)
from shared.domain.response.responses import ApiResponse

router = APIRouter(prefix="/api/banner-command", tags=["banner-command"])


def get_banner_handler(request: Request) -> BannerHandler:
    return BannerHandler(request.app.state.connections)


@router.post("/create")
async def create_banner(
    request: Request,
    body: CreateBannerRequest,
) -> ApiResponse[BannerResponse]:
    return await get_banner_handler(request).create(
        body.name,
        body.start_date,
        body.end_date,
        body.start_time,
        body.end_time,
        body.is_active,
    )


# Static paths first — `/restore/all` must not be captured as
# banner_id="all" by `/restore/{banner_id}`.
@router.post("/restore/all")
async def restore_all_banner(request: Request) -> ApiResponse[None]:
    return await get_banner_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_banner_permanent(request: Request) -> ApiResponse[None]:
    return await get_banner_handler(request).delete_all_permanent()


@router.post("/update/{banner_id}")
async def update_banner(
    request: Request,
    banner_id: int,
    body: UpdateBannerRequest,
) -> ApiResponse[BannerResponse]:
    return await get_banner_handler(request).update(
        banner_id,
        body.name,
        body.start_date,
        body.end_date,
        body.start_time,
        body.end_time,
        body.is_active,
    )


@router.post("/trashed/{banner_id}")
async def trash_banner(
    request: Request,
    banner_id: int,
) -> ApiResponse[BannerResponseDeleteAt]:
    return await get_banner_handler(request).trash(banner_id)


@router.post("/restore/{banner_id}")
async def restore_banner(
    request: Request,
    banner_id: int,
) -> ApiResponse[BannerResponseDeleteAt]:
    return await get_banner_handler(request).restore(banner_id)


@router.delete("/permanent/{banner_id}")
async def delete_banner_permanent(
    request: Request,
    banner_id: int,
) -> ApiResponse[None]:
    return await get_banner_handler(request).delete_permanent(banner_id)


__all__ = ["router"]
