"""Banner request DTOs. Validation Matches the expected `validator` tags: a non-empty `name`, and `datetime=2006-01-02` / `datetime=15:04:05` for the date and time fields (the same shapes the repository later parses with `utils.ParseDate` / `utils.ParseTime`)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


def _validate_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("must be in YYYY-MM-DD format") from exc
    return value


def _validate_time(value: str) -> str:
    try:
        datetime.strptime(value, "%H:%M:%S")
    except ValueError as exc:
        raise ValueError("must be in HH:MM:SS format") from exc
    return value


class FindAllBanner(BaseModel):
    search: str = ""
    page: int = 1
    page_size: int = 10

    @model_validator(mode="after")
    def _clamp_pagination(self) -> FindAllBanner:
        if self.page <= 0:
            self.page = 1
        if self.page_size <= 0:
            self.page_size = 10
        if self.page_size > 100:
            self.page_size = 100
        return self


class CreateBannerRequest(BaseModel):
    name: str = Field(..., min_length=1)
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    is_active: bool = False

    @field_validator("start_date", "end_date")
    @classmethod
    def _check_date(cls, value: str) -> str:
        return _validate_date(value)

    @field_validator("start_time", "end_time")
    @classmethod
    def _check_time(cls, value: str) -> str:
        return _validate_time(value)


class UpdateBannerRequest(BaseModel):
    banner_id: int | None = None
    name: str = Field(..., min_length=1)
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    is_active: bool = False

    @field_validator("start_date", "end_date")
    @classmethod
    def _check_date(cls, value: str) -> str:
        return _validate_date(value)

    @field_validator("start_time", "end_time")
    @classmethod
    def _check_time(cls, value: str) -> str:
        return _validate_time(value)


__all__ = ["CreateBannerRequest", "FindAllBanner", "UpdateBannerRequest"]
