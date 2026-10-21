"""Review command REST routes. binds a JSON body and validates it (`CreateReviewRequest`/`UpdateReviewRequest`); reuses the shared pydantic DTOs, so an invalid body yields the global 400 `"Validation failed"` envelope rather than FastAPI's 422. `Create` returns 201 (`http.StatusCreated`) and takes the author id from the JWT (`request.state.user_id`), ignoring the body's `user_id`. `Update` takes the path id and ignores the body's `review_id`/`name`,. Static `/restore/all` and `/permanent/all` are registered before the `/restore/{review_id}` variant because Starlette matches routes in registration order (Echo prioritises static segments). The gateway does not cache."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from service.apigateway.handler.review.handler import ReviewHandler
from shared.domain.requests.review import (
    CreateReviewRequest,
    UpdateReviewRequest,
)
from shared.domain.response.responses import ApiResponse
from shared.domain.response.review import (
    ReviewResponse,
    ReviewResponseDeleteAt,
)

router = APIRouter(prefix="/api/review-command", tags=["review-command"])


def get_review_handler(request: Request) -> ReviewHandler:
    return ReviewHandler(request.app.state.connections)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_review(
    request: Request,
    body: CreateReviewRequest,
) -> ApiResponse[ReviewResponse]:
    return await get_review_handler(request).create(
        getattr(request.state, "user_id", None),
        body.product_id,
        body.rating,
        body.comment,
    )


# Static paths first — `/restore/all` must not be captured as review_id="all".
@router.post("/restore/all")
async def restore_all_review(request: Request) -> ApiResponse[None]:
    return await get_review_handler(request).restore_all()


@router.post("/permanent/all")
async def delete_all_review_permanent(request: Request) -> ApiResponse[None]:
    return await get_review_handler(request).delete_all_permanent()


@router.post("/update/{review_id}")
async def update_review(
    request: Request,
    review_id: int,
    body: UpdateReviewRequest,
) -> ApiResponse[ReviewResponse]:
    return await get_review_handler(request).update(review_id, body.rating, body.comment)


@router.post("/trashed/{review_id}")
async def trash_review(
    request: Request,
    review_id: int,
) -> ApiResponse[ReviewResponseDeleteAt]:
    return await get_review_handler(request).trash(review_id)


@router.post("/restore/{review_id}")
async def restore_review(
    request: Request,
    review_id: int,
) -> ApiResponse[ReviewResponseDeleteAt]:
    return await get_review_handler(request).restore(review_id)


@router.delete("/permanent/{review_id}")
async def delete_review_permanent(
    request: Request,
    review_id: int,
) -> ApiResponse[None]:
    return await get_review_handler(request).delete_permanent(review_id)


__all__ = ["router"]
