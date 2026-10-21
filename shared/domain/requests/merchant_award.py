"""merchant_award request DTOs. Validation Matches the expected `validator` tags: - create: `merchant_id` (`required` → non-zero), `title`, `description`, `issued_by` required; `issue_date` (`required,datetime=2006-01-02`) must be a bare `YYYY-MM-DD` date; `expiry_date` (`omitempty,datetime=2006-01-02`) optional but, when present, must be the same format; `certificate_url` (`omitempty,url`) must be empty or a URL; - update: same fields plus `merchant_certification_id` (`required`), which the caller supplies (the gRPC handler / gateway attaches it). `datetime=2006-01-02` layout is exact: `2020-1-5` or a full RFC3339 timestamp are rejected. enforces the same via a strict regex plus a real-calendar check (Python's `date.fromisoformat` accepts only zero-padded ISO dates, matching the layout)."""

from __future__ import annotations

import re
from datetime import date

from pydantic import BaseModel, Field, field_validator

# `url` tag accepts any scheme as long as a host follows; a bare
# `example.com` or `not-a-url` is rejected.
_URL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/]+")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _check_url(value: str) -> str:
    if value == "":
        return value
    if not _URL_RE.match(value):
        raise ValueError("must be a valid URL")
    return value


def _check_date(value: str, *, allow_empty: bool) -> str:
    if value == "" and allow_empty:
        return value
    if not _DATE_RE.match(value):
        raise ValueError("must be a date in YYYY-MM-DD format")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("must be a valid date") from exc
    return value


class CreateMerchantCertificationOrAwardRequest(BaseModel):
    merchant_id: int = Field(..., ge=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    issued_by: str = Field(..., min_length=1)
    issue_date: str
    expiry_date: str = ""
    certificate_url: str = ""

    @field_validator("issue_date")
    @classmethod
    def _validate_issue_date(cls, value: str) -> str:
        return _check_date(value, allow_empty=False)

    @field_validator("expiry_date")
    @classmethod
    def _validate_expiry_date(cls, value: str) -> str:
        return _check_date(value, allow_empty=True)

    @field_validator("certificate_url")
    @classmethod
    def _validate_certificate_url(cls, value: str) -> str:
        return _check_url(value)


class UpdateMerchantCertificationOrAwardRequest(BaseModel):
    merchant_certification_id: int | None = None
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    issued_by: str = Field(..., min_length=1)
    issue_date: str
    expiry_date: str = ""
    certificate_url: str = ""

    @field_validator("issue_date")
    @classmethod
    def _validate_issue_date(cls, value: str) -> str:
        return _check_date(value, allow_empty=False)

    @field_validator("expiry_date")
    @classmethod
    def _validate_expiry_date(cls, value: str) -> str:
        return _check_date(value, allow_empty=True)

    @field_validator("certificate_url")
    @classmethod
    def _validate_certificate_url(cls, value: str) -> str:
        return _check_url(value)


__all__ = [
    "CreateMerchantCertificationOrAwardRequest",
    "UpdateMerchantCertificationOrAwardRequest",
]
