"""Slider query REST routes.

Static paths (`/active`, `/trashed`) are registered before `/{slider_id}`
because Starlette matches routes in registration order (unlike chi, which
prioritises static segments). Without this ordering `/active` would be
captured as slider_id="active"."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.slider.handler import SliderHandler
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.domain.response.slider import SliderResponse, SliderResponseDeleteAt

router = APIRouter(prefix="/api/slider-query", tags=["slider-query"])


def get_slider_handler(request: Request) -> SliderHandler:
    return SliderHandler(request.app.state.connections, request.app.state.upload_image)


@router.get("")
async def find_all_slider(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[SliderResponse]]:
    return await get_slider_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_slider(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[SliderResponseDeleteAt]]:
    return await get_slider_handler(request).find_by_active(page, page_size, search)


@router.get("/trashed")
async def find_trashed_slider(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[SliderResponseDeleteAt]]:
    return await get_slider_handler(request).find_by_trashed(page, page_size, search)


@router.get("/{slider_id}")
async def find_slider_by_id(
    request: Request,
    slider_id: int,
) -> ApiResponse[SliderResponse]:
    return await get_slider_handler(request).find_by_id(slider_id)


__all__ = ["router"]
