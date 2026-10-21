"""Row types for the sliders table. Timestamps surface as `datetime.datetime`; the handlers format them as date-only strings (`%Y-%m-%d`) to match the `2006-01-02` layout."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Slider:

    slider_id: int
    name: str
    image: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> Slider:
        return cls(
            slider_id=row["slider_id"],
            name=row["name"],
            image=row["image"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateSliderRow:
    slider_id: int
    name: str
    image: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateSliderRow:
        return cls(
            slider_id=row["slider_id"],
            name=row["name"],
            image=row["image"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class GetSliderByIDRow:
    """`FindById` projection — active rows only, no `deleted_at`."""

    slider_id: int
    name: str
    image: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetSliderByIDRow:
        return cls(
            slider_id=row["slider_id"],
            name=row["name"],
            image=row["image"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


UpdateSliderRow = GetSliderByIDRow


@dataclass
class GetSlidersRow:
    """`FindAll` projection with a window total count (active rows only)."""

    slider_id: int
    name: str
    image: str
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetSlidersRow:
        return cls(
            slider_id=row["slider_id"],
            name=row["name"],
            image=row["image"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetSlidersActiveRow:
    slider_id: int
    name: str
    image: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetSlidersActiveRow:
        return cls(
            slider_id=row["slider_id"],
            name=row["name"],
            image=row["image"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


GetSlidersTrashedRow = GetSlidersActiveRow


__all__ = [
    "CreateSliderRow",
    "GetSliderByIDRow",
    "GetSlidersActiveRow",
    "GetSlidersRow",
    "GetSlidersTrashedRow",
    "Slider",
    "UpdateSliderRow",
]
