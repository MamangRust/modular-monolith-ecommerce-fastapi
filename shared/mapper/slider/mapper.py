"""Slider row/proto -> response DTO mapping. Two input shapes, one output: - row dataclasses — format the timestamp values as date-only strings (`%Y-%m-%d`) to match the `2006-01-02` layout; - proto messages — already-formatted date-only strings, passed through unchanged."""

from __future__ import annotations

from typing import Any

from pkg.database.schema.slider import (
    CreateSliderRow,
    GetSliderByIDRow,
    GetSlidersActiveRow,
    GetSlidersRow,
    Slider,
    UpdateSliderRow,
)
from shared.convert.convert import format_date
from shared.domain.response.slider import SliderResponse, SliderResponseDeleteAt

SliderRow = (
    Slider
    | CreateSliderRow
    | GetSliderByIDRow
    | GetSlidersRow
    | UpdateSliderRow
)
SliderDeleteAtRow = Slider | GetSlidersActiveRow


def to_slider_response(row: SliderRow) -> SliderResponse:
    return SliderResponse(
        id=row.slider_id,
        name=row.name,
        image=row.image,
        created_at=format_date(row.created_at),
        updated_at=format_date(row.updated_at),
    )


def to_slider_response_delete_at(row: SliderDeleteAtRow) -> SliderResponseDeleteAt:
    return SliderResponseDeleteAt(
        id=row.slider_id,
        name=row.name,
        image=row.image,
        created_at=format_date(row.created_at),
        updated_at=format_date(row.updated_at),
        deleted_at=format_date(row.deleted_at) or None,
    )


def map_slider_response(pb: Any) -> SliderResponse:
    return SliderResponse(
        id=int(pb.id),
        name=pb.name,
        image=pb.image,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_slider_response_delete_at(pb: Any) -> SliderResponseDeleteAt:
    # always sets the pointer, so an absent wrapper renders as "".
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return SliderResponseDeleteAt(
        id=int(pb.id),
        name=pb.name,
        image=pb.image,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
    )


__all__ = [
    "map_slider_response",
    "map_slider_response_delete_at",
    "to_slider_response",
    "to_slider_response_delete_at",
]
