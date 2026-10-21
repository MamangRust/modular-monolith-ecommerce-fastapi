"""Unit tests for the slider response mapper. Covers both input shapes: row dataclasses (which the mapper formats to date-only strings) and proto messages (which it passes through). The REST shape carries `id`, `name`, `image`, `created_at`, `updated_at` — there is no cost/courier like shipping_address. An absent `deleted_at` wrapper renders as `""` (the slider command mapper always sets the pointer)."""

from __future__ import annotations

from datetime import datetime

from pb.slider import slider_common_pb2
from pkg.database.schema.slider import (
    CreateSliderRow,
    GetSliderByIDRow,
    GetSlidersActiveRow,
    GetSlidersRow,
    Slider,
)
from shared.mapper.slider import (
    map_pagination_meta,
    map_slider_response,
    map_slider_response_delete_at,
    to_api_response_pagination_slider,
    to_api_response_pagination_slider_delete_at,
    to_api_response_slider,
    to_api_response_slider_all,
    to_api_response_slider_delete,
    to_api_response_slider_delete_at,
    to_slider_response,
    to_slider_response_delete_at,
)

CREATED = datetime(2026, 1, 2)
UPDATED = datetime(2026, 1, 3)
DELETED = datetime(2026, 2, 1)


def _row(slider_id: int = 1, total: int = 1) -> GetSlidersRow:
    return GetSlidersRow(
        slider_id=slider_id,
        name="Hero",
        image="/img/a.png",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row() -> GetSlidersActiveRow:
    return GetSlidersActiveRow(
        slider_id=2,
        name="Banner",
        image="/img/b.png",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=DELETED,
        total_count=1,
    )


def test_row_mapping_formats_date_only() -> None:
    result = to_slider_response(_row())
    assert result.id == 1
    assert result.name == "Hero"
    assert result.image == "/img/a.png"
    assert result.created_at == "2026-01-02"
    assert result.updated_at == "2026-01-03"
    assert not hasattr(result, "courier")


def test_row_mapping_delete_at_includes_deleted_at() -> None:
    result = to_slider_response_delete_at(_active_row())
    assert result.id == 2
    assert result.name == "Banner"
    assert result.deleted_at == "2026-02-01"


def test_row_mapping_accepts_all_row_shapes() -> None:
    create_row = CreateSliderRow(
        slider_id=3,
        name="c",
        image="/c.png",
        created_at=CREATED,
        updated_at=UPDATED,
    )
    by_id = GetSliderByIDRow(
        slider_id=4,
        name="d",
        image="/d.png",
        created_at=CREATED,
        updated_at=UPDATED,
    )
    full = Slider(
        slider_id=6,
        name="f",
        image="/f.png",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
    )
    assert to_slider_response(create_row).id == 3
    assert to_slider_response(by_id).name == "d"
    # A restored row carries a None deleted_at; the row mapper keeps it None
    # (the gRPC handler re-derives the wrapper, and the proto mapper uses "").
    assert to_slider_response_delete_at(full).deleted_at is None


def _proto_slider() -> slider_common_pb2.SliderResponse:
    return slider_common_pb2.SliderResponse(
        id=7,
        name="Hero",
        image="/img/a.png",
        created_at="2026-05-06",
        updated_at="2026-05-07",
    )


def test_proto_mapping_passes_strings_through() -> None:
    message = slider_common_pb2.ApiResponseSlider(status="success", message="ok")
    message.data.CopyFrom(_proto_slider())
    dumped = to_api_response_slider(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "name": "Hero",
        "image": "/img/a.png",
        "created_at": "2026-05-06",
        "updated_at": "2026-05-07",
    }


def test_proto_delete_at_missing_renders_empty_string() -> None:
    message = slider_common_pb2.SliderResponseDeleteAt(id=1)
    mapped = map_slider_response_delete_at(message)
    assert mapped.deleted_at == ""


def test_proto_delete_at_present_passes_through() -> None:
    message = slider_common_pb2.SliderResponseDeleteAt(id=1)
    message.deleted_at.value = "2026-02-03"
    mapped = map_slider_response_delete_at(message)
    assert mapped.deleted_at == "2026-02-03"


def test_proto_response_mapping_uses_rest_field_id() -> None:
    mapped = map_slider_response(_proto_slider())
    assert mapped.id == 7
    assert mapped.image == "/img/a.png"


def test_pagination_mapping() -> None:
    message = slider_common_pb2.ApiResponsePaginationSlider(
        status="success", message="ok"
    )
    message.data.add(id=1, name="Hero", image="/a.png")
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_slider(message).model_dump()
    assert dumped["data"][0]["name"] == "Hero"
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_trashed_pagination_delete_at() -> None:
    message = slider_common_pb2.ApiResponsePaginationSliderDeleteAt(
        status="success", message="ok"
    )
    message.data.add(id=9, name="Hero", image="/a.png")
    message.data[0].deleted_at.value = "2026-02-03"
    dumped = to_api_response_pagination_slider_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03"


def test_delete_envelope_has_no_data() -> None:
    message = slider_common_pb2.ApiResponseSliderDelete(
        status="success", message="deleted"
    )
    dumped = to_api_response_slider_delete(message).model_dump()
    assert dumped == {"status": "success", "message": "deleted", "data": None}


def test_all_envelope_has_no_data() -> None:
    message = slider_common_pb2.ApiResponseSliderAll(
        status="success", message="restored"
    )
    dumped = to_api_response_slider_all(message).model_dump()
    assert dumped == {"status": "success", "message": "restored", "data": None}


def test_command_delete_at_envelope() -> None:
    message = slider_common_pb2.ApiResponseSliderDeleteAt(
        status="success", message="ok"
    )
    message.data.id = 1
    message.data.name = "Hero"
    message.data.image = "/a.png"
    dumped = to_api_response_slider_delete_at(message).model_dump()
    assert dumped["data"]["id"] == 1
    # Absent wrapper still renders as "".
    assert dumped["data"]["deleted_at"] == ""


def test_map_pagination_meta_none_defaults() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


__all__ = []
