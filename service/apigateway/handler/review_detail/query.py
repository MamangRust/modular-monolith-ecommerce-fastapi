"""Review detail query REST routes.

Static paths (`/active`, `/trashed`) are registered before `/{review_detail_id}`
because Starlette matches routes in registration order (unlike chi, which
prioritises static segments). Without this ordering `/active` would be captured
as review_detail_id="active"."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.review_detail.handler import ReviewDetailHandler
from shared.domain.response.responses import ApiResponse, APIResponsePagination
from shared.domain.response.review_detail import (
    ReviewDetailResponse,
    ReviewDetailResponseDeleteAt,
)

router = APIRouter(prefix="/api/review-detail-query", tags=["review-detail-query"])


def get_review_detail_handler(request: Request) -> ReviewDetailHandler:
    return ReviewDetailHandler(
        request.app.state.connections, request.app.state.upload_image
    )


@router.get("")
async def find_all_review_detail(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ReviewDetailResponse]]:
    return await get_review_detail_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_review_detail(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ReviewDetailResponseDeleteAt]]:
    return await get_review_detail_handler(request).find_by_active(
        page, page_size, search
    )


@router.get("/trashed")
async def find_trashed_review_detail(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ReviewDetailResponseDeleteAt]]:
    return await get_review_detail_handler(request).find_by_trashed(
        page, page_size, search
    )


@router.get("/{review_detail_id}")
async def find_review_detail_by_id(
    request: Request,
    review_detail_id: int,
) -> ApiResponse[ReviewDetailResponse]:
    return await get_review_detail_handler(request).find_by_id(review_detail_id)


__all__ = ["router"]
