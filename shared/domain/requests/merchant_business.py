"""merchant_business request DTOs. Validation Matches the expected `validator` tags: - create: `merchant_id` (`required` → non-zero), `business_type`, `tax_id` required; `established_year` (`required,min=1900,max=2100`); `number_of_employees` (`required,min=1`); `website_url` (`omitempty,url`) must be empty or a URL; - update: same fields plus `merchant_business_info_id` (`required`), which the caller supplies (the gRPC handler / gateway attaches it). `url` tag accepts any scheme as long as a host follows; a bare `example.com` or `not-a-url` is rejected."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator

_URL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/]+")


def _check_url(value: str) -> str:
    if value == "":
        return value
    if not _URL_RE.match(value):
        raise ValueError("must be a valid URL")
    return value


class CreateMerchantBusinessInformationRequest(BaseModel):
    merchant_id: int = Field(..., ge=1)
    business_type: str = Field(..., min_length=1)
    tax_id: str = Field(..., min_length=1)
    established_year: int = Field(..., ge=1900, le=2100)
    number_of_employees: int = Field(..., ge=1)
    website_url: str = ""

    @field_validator("website_url")
    @classmethod
    def _validate_website_url(cls, value: str) -> str:
        return _check_url(value)


class UpdateMerchantBusinessInformationRequest(BaseModel):
    merchant_business_info_id: int | None = None
    business_type: str = Field(..., min_length=1)
    tax_id: str = Field(..., min_length=1)
    established_year: int = Field(..., ge=1900, le=2100)
    number_of_employees: int = Field(..., ge=1)
    website_url: str = ""

    @field_validator("website_url")
    @classmethod
    def _validate_website_url(cls, value: str) -> str:
        return _check_url(value)


__all__ = [
    "CreateMerchantBusinessInformationRequest",
    "UpdateMerchantBusinessInformationRequest",
]
