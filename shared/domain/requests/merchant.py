"""Merchant request DTOs. Validation Matches the expected `validator` tags: - merchant create/update: `name`, `description`, `address`, `contact_email` (email), `contact_phone`, `status` are `required` (non-empty); - merchant document create: `merchant_id` (`required,min=1`), `document_type`, `document_url` required; - document update / update-status: `merchant_id` (`min=1`), `status` and `note` required (the handler maps a validation failure to a 500, see the handler module); - pagination clamps like the handler (page <= 0 -> 1, page_size <= 0 -> 10, page_size capped at 100). `user_id` on the merchant create/update DTO is accepted from the body but ignored: the handler takes the owner id from the JWT context (does the same). The `email` check is a regex rather than pydantic's `EmailStr` so not pull in `email-validator` (same choice as user/auth)."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class FindAllMerchant(BaseModel):
    search: str = ""
    page: int = 1
    page_size: int = 10

    @model_validator(mode="after")
    def _clamp_pagination(self) -> FindAllMerchant:
        if self.page <= 0:
            self.page = 1
        if self.page_size <= 0:
            self.page_size = 10
        if self.page_size > 100:
            self.page_size = 100
        return self


class CreateMerchantRequest(BaseModel):
    user_id: int = 0
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    contact_email: str = Field(..., pattern=_EMAIL)
    contact_phone: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)


class UpdateMerchantRequest(BaseModel):
    merchant_id: int | None = None
    user_id: int = 0
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    contact_email: str = Field(..., pattern=_EMAIL)
    contact_phone: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)


class UpdateMerchantStatusRequest(BaseModel):
    merchant_id: int | None = None
    status: str = Field(..., min_length=1)


# ---- merchant documents ----


class FindAllMerchantDocuments(BaseModel):
    search: str = ""
    page: int = 1
    page_size: int = 10

    @model_validator(mode="after")
    def _clamp_pagination(self) -> FindAllMerchantDocuments:
        if self.page <= 0:
            self.page = 1
        if self.page_size <= 0:
            self.page_size = 10
        if self.page_size > 100:
            self.page_size = 100
        return self


class CreateMerchantDocumentRequest(BaseModel):
    merchant_id: int = Field(..., ge=1)
    document_type: str = Field(..., min_length=1)
    document_url: str = Field(..., min_length=1)


class UpdateMerchantDocumentRequest(BaseModel):
    document_id: int | None = None
    merchant_id: int = Field(..., ge=1)
    document_type: str = Field(..., min_length=1)
    document_url: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)
    note: str = Field(..., min_length=1)


class UpdateMerchantDocumentStatusRequest(BaseModel):
    document_id: int | None = None
    merchant_id: int = Field(..., ge=1)
    status: str = Field(..., min_length=1)
    note: str = Field(..., min_length=1)


__all__ = [
    "CreateMerchantDocumentRequest",
    "CreateMerchantRequest",
    "FindAllMerchant",
    "FindAllMerchantDocuments",
    "UpdateMerchantDocumentRequest",
    "UpdateMerchantDocumentStatusRequest",
    "UpdateMerchantRequest",
    "UpdateMerchantStatusRequest",
]
