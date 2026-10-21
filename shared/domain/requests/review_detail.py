"""Review detail request DTOs. the `CreateReviewDetailRequest` / `UpdateReviewDetailRequest` carry no `validate` struct tags, so `Validate` is a no-op. The gateway's own multipart-form checks (`review_id`, `type`, `caption`) live in the gateway handler, not here; these DTOs are the domain-service inputs. keeps the same shape (review_id + type + url + caption) without pydantic validators, that behaviour. `caption` is optional (`*string`)."""

from __future__ import annotations

from pydantic import BaseModel


class FindAllReviewDetail(BaseModel):
    search: str = ""
    page: int = 1
    page_size: int = 10


class CreateReviewDetailRequest(BaseModel):
    review_id: int
    type: str
    url: str
    caption: str | None = None


class UpdateReviewDetailRequest(BaseModel):
    review_detail_id: int | None = None
    type: str
    url: str
    caption: str | None = None


__all__ = [
    "CreateReviewDetailRequest",
    "FindAllReviewDetail",
    "UpdateReviewDetailRequest",
]
