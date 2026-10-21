"""merchant_detail request DTOs. models that as a required `int` (no default): omission → 400, `0` → accepted. The URL check is a regex rather than pydantic's `AnyUrl` so keeps the `url` tag semantics (scheme + host required, any scheme) and does not pull in `email-validator`/`pydantic[url]`."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator

# `url` tag accepts any scheme as long as a host follows; a bare
# `example.com` or `not-a-url` is rejected.
_URL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/]+")


def _check_url(value: str, *, allow_empty: bool) -> str:
    if value == "" and allow_empty:
        return value
    if not _URL_RE.match(value):
        raise ValueError("must be a valid URL")
    return value


class CreateMerchantDetailRequest(BaseModel):
    merchant_id: int = Field(..., ge=1)
    display_name: str = Field(..., min_length=1)
    cover_image_url: str = ""
    logo_url: str = ""
    short_description: str = Field(..., min_length=1)
    website_url: str = ""

    @field_validator("website_url")
    @classmethod
    def _validate_website_url(cls, value: str) -> str:
        return _check_url(value, allow_empty=True)


class UpdateMerchantDetailRequest(BaseModel):
    merchant_detail_id: int | None = None
    display_name: str = Field(..., min_length=1)
    cover_image_url: str = ""
    logo_url: str = ""
    short_description: str = Field(..., min_length=1)
    website_url: str = ""

    @field_validator("website_url")
    @classmethod
    def _validate_website_url(cls, value: str) -> str:
        return _check_url(value, allow_empty=True)


class CreateMerchantSocialRequest(BaseModel):
    merchant_detail_id: int
    platform: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)

    @field_validator("url")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        return _check_url(value, allow_empty=False)


class UpdateMerchantSocialRequest(BaseModel):
    id: int = 0
    merchant_detail_id: int
    platform: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)

    @field_validator("url")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        return _check_url(value, allow_empty=False)


__all__ = [
    "CreateMerchantDetailRequest",
    "CreateMerchantSocialRequest",
    "UpdateMerchantDetailRequest",
    "UpdateMerchantSocialRequest",
]
