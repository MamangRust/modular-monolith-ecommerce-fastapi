"""Slider request DTOs. Unlike banner, the `CreateSliderRequest` / `UpdateSliderRequest` carry no `validate` struct tags, so `Validate` is a no-op. The gateway's own multipart-form checks (`name` required, `image` required on create) live in the gateway handler, not here. keeps the same shape (name + image) without pydantic validators, that behaviour. The `FindAllSlider` pagination is clamped in the handler/service, not here."""

from __future__ import annotations

from pydantic import BaseModel


class FindAllSlider(BaseModel):
    search: str = ""
    page: int = 1
    page_size: int = 10


class CreateSliderRequest(BaseModel):
    name: str
    image: str


class UpdateSliderRequest(BaseModel):
    slider_id: int | None = None
    name: str
    image: str


__all__ = ["CreateSliderRequest", "FindAllSlider", "UpdateSliderRequest"]
