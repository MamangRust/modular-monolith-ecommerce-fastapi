"""Unit tests for the banner response mapper.

Covers both input shapes: row dataclasses (which the mapper formats) and
proto messages (which it passes through). The banner timestamp layout
(`%Y-%m-%d %H:%M:%S.mmm`) is deliberately different from role/user, so it
is asserted explicitly.
"""

from __future__ import annotations

from datetime import date, datetime, time

from pb.banner import banner_common_pb2
from pkg.database.schema.banner import (
    Banner,
    CreateBannerRow,
    GetBannerRow,
    GetBannersActiveRow,
    GetBannersRow,
)
from shared.mapper.banner import (
    map_banner_response,
    map_banner_response_delete_at,
    map_pagination_meta,
    to_api_response_banner,
    to_api_response_pagination_banner,
    to_api_response_pagination_banner_delete_at,
    to_banner_response,
    to_banner_response_delete_at,
)

CREATED = datetime(2026, 1, 2, 3, 4, 5, 123456)
UPDATED = datetime(2026, 1, 3, 4, 5, 6, 654321)
DELETED = datetime(2026, 2, 1, 10, 0, 0, 500000)


def _row() -> GetBannersRow:
    return GetBannersRow(
        banner_id=1,
        name="Banner 1",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31),
        start_time=time(8, 0),
        end_time=time(16, 0),
        is_active=True,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=1,
    )


def _active_row() -> GetBannersActiveRow:
    return GetBannersActiveRow(
        banner_id=2,
        name="Banner 2",
        start_date=date(2023, 2, 1),
        end_date=date(2023, 2, 28),
        start_time=time(9, 0),
        end_time=time(17, 0),
        is_active=False,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=DELETED,
        total_count=1,
    )


def test_row_mapping_formats_banner_timestamps() -> None:
    result = to_banner_response(_row())
    assert result.id == 1
    assert result.start_date == "2023-01-01"
    assert result.end_date == "2023-01-31"
    assert result.start_time == "08:00:00"
    assert result.end_time == "16:00:00"
    assert result.created_at == "2026-01-02 03:04:05.123"
    assert result.updated_at == "2026-01-03 04:05:06.654"
    assert result.is_active is True


def test_row_mapping_delete_at_includes_deleted_at() -> None:
    result = to_banner_response_delete_at(_active_row())
    assert result.id == 2
    assert result.deleted_at == "2026-02-01 10:00:00.500"


def test_row_mapping_accepts_all_row_shapes() -> None:
    create_row = CreateBannerRow(
        banner_id=3,
        name="B",
        start_date=date(2023, 3, 1),
        end_date=date(2023, 3, 31),
        start_time=time(10, 0),
        end_time=time(18, 0),
        is_active=False,
        created_at=CREATED,
        updated_at=UPDATED,
    )
    banner = Banner(
        banner_id=4,
        name="C",
        start_date=date(2023, 4, 1),
        end_date=date(2023, 4, 30),
        start_time=time(7, 0),
        end_time=time(15, 0),
        is_active=True,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
    )
    assert to_banner_response(create_row).start_time == "10:00:00"
    assert to_banner_response(banner).id == 4


def _proto_banner() -> banner_common_pb2.BannerResponse:
    message = banner_common_pb2.ApiResponseBanner(status="success", message="ok")
    message.data.banner_id = 7
    message.data.name = "Proto"
    message.data.start_date = "2023-05-01"
    message.data.end_date = "2023-05-31"
    message.data.start_time = "06:00:00"
    message.data.end_time = "14:00:00"
    message.data.is_active = True
    message.data.created_at = "2026-05-06 07:08:09.101"
    message.data.updated_at = "2026-05-07 08:09:10.202"
    return message


def test_proto_mapping_passes_strings_through_unchanged() -> None:
    dumped = to_api_response_banner(_proto_banner()).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "name": "Proto",
        "start_date": "2023-05-01",
        "end_date": "2023-05-31",
        "start_time": "06:00:00",
        "end_time": "14:00:00",
        "is_active": True,
        "created_at": "2026-05-06 07:08:09.101",
        "updated_at": "2026-05-07 08:09:10.202",
    }


def test_proto_mapping_uses_rest_field_id() -> None:
    response = banner_common_pb2.ApiResponseBanner(status="success", message="ok")
    response.data.banner_id = 9
    mapped = map_banner_response(response.data)
    assert mapped.id == 9


def test_proto_delete_at_missing_renders_empty_string() -> None:
    message = banner_common_pb2.ApiResponseBannerDeleteAt(status="success", message="ok")
    message.data.banner_id = 1
    mapped = map_banner_response_delete_at(message.data)
    assert mapped.deleted_at == ""


def test_proto_delete_at_present_passes_through() -> None:
    message = banner_common_pb2.ApiResponseBannerDeleteAt(status="success", message="ok")
    message.data.banner_id = 1
    message.data.deleted_at.value = "2026-02-03 04:05:06.700"
    mapped = map_banner_response_delete_at(message.data)
    assert mapped.deleted_at == "2026-02-03 04:05:06.700"


def test_pagination_mapping() -> None:
    message = banner_common_pb2.ApiResponsePaginationBanner(status="success", message="ok")
    row = message.data.add(banner_id=1, name="A", created_at="2026-01-01")
    row.start_date = "2023-01-01"
    row.end_date = "2023-01-31"
    row.start_time = "08:00:00"
    row.end_time = "16:00:00"
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_banner(message).model_dump()
    assert dumped["data"][0]["name"] == "A"
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_trashed_pagination_delete_at() -> None:
    message = banner_common_pb2.ApiResponsePaginationBannerDeleteAt(
        status="success", message="ok"
    )
    message.data.add(banner_id=9, name="Trashed")
    message.data[0].deleted_at.value = "2026-02-03 00:00:00.000"
    dumped = to_api_response_pagination_banner_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03 00:00:00.000"


def test_map_pagination_meta_none_defaults_to_zero() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


def test_get_banner_row_shares_shape() -> None:
    row = GetBannerRow(
        banner_id=5,
        name="B",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31),
        start_time=time(8, 0),
        end_time=time(16, 0),
        is_active=True,
        created_at=CREATED,
        updated_at=UPDATED,
    )
    assert to_banner_response(row).id == 5
