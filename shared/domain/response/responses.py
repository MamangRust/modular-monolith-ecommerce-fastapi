"""Generic response envelopes."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    current_page: int = 1
    page_size: int = 10
    total_pages: int = 0
    total_records: int = 0


class ApiResponse(BaseModel, Generic[T]):
    status: str
    message: str
    data: T | None = None


class APIResponsePagination(BaseModel, Generic[T]):
    status: str
    message: str
    data: T | None = None
    pagination: PaginationMeta = PaginationMeta()


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str = ""
    code: int = 500
