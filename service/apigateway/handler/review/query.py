"""Review query REST routes.

Static `/active` and `/trashed` are registered before the `/product/{id}` and
`/merchant/{id}` routes for readability, though their static prefixes already
disambiguate them. The gateway does not cache."""

from __future__ import annotations

from fastapi import APIRouter, Request

from service.apigateway.handler.review.handler import ReviewHandler
from shared.domain.response.responses import APIResponsePagination
from shared.domain.response.review import (
    ReviewResponse,
    ReviewResponseDeleteAt,
    ReviewsDetailResponse,
)

router = APIRouter(prefix="/api/review-query", tags=["review-query"])


def get_review_handler(request: Request) -> ReviewHandler:
    return ReviewHandler(request.app.state.connections)


@router.get("")
async def find_all_review(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ReviewResponse]]:
    return await get_review_handler(request).find_all(page, page_size, search)


@router.get("/active")
async def find_active_review(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ReviewResponseDeleteAt]]:
    return await get_review_handler(request).find_by_active(page, page_size, search)


@router.get("/trashed")
async def find_trashed_review(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ReviewResponseDeleteAt]]:
    return await get_review_handler(request).find_by_trashed(page, page_size, search)


@router.get("/product/{product_id}")
async def find_reviews_by_product(
    request: Request,
    product_id: int,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ReviewsDetailResponse]]:
    return await get_review_handler(request).find_by_product(product_id, page, page_size, search)


@router.get("/merchant/{merchant_id}")
async def find_reviews_by_merchant(
    request: Request,
    merchant_id: int,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
) -> APIResponsePagination[list[ReviewsDetailResponse]]:
    return await get_review_handler(request).find_by_merchant(merchant_id, page, page_size, search)


__all__ = ["router"]
