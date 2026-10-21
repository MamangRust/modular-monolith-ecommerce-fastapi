"""Unit tests for the category response mapper.

Covers both input shapes: row dataclasses (formatted `%Y-%m-%d`) and proto
messages (passed through). The category date layout differs from banner's
millisecond layout, so it is asserted explicitly.
"""

from __future__ import annotations

from datetime import datetime

from pb.category import category_common_pb2
from pkg.database.schema.category import (
    Category,
    CreateCategoryRow,
    GetCategoriesActiveRow,
    GetCategoriesRow,
    GetCategoryByIDRow,
)
from shared.mapper.category import (
    map_category_response,
    map_category_response_delete_at,
    map_pagination_meta,
    to_api_response_category,
    to_api_response_category_month_price,
    to_api_response_category_monthly_total_price,
    to_api_response_category_year_price,
    to_api_response_category_yearly_total_price,
    to_api_response_pagination_category,
    to_api_response_pagination_category_delete_at,
    to_category_response,
    to_category_response_delete_at,
)

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 1, 10, 0, 0)


def _row() -> GetCategoriesRow:
    return GetCategoriesRow(
        category_id=1,
        name="Elektronik",
        description="desc",
        slug_category="elektronik",
        image_category="elektronik.png",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=1,
    )


def _active_row(deleted_at: datetime | None = DELETED) -> GetCategoriesActiveRow:
    return GetCategoriesActiveRow(
        category_id=2,
        name="Fashion",
        description="desc",
        slug_category="fashion",
        image_category="fashion.png",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        total_count=1,
    )


def test_row_mapping_formats_category_dates() -> None:
    result = to_category_response(_row())
    assert result.id == 1
    assert result.name == "Elektronik"
    assert result.created_at == "2026-01-02"
    assert result.updated_at == "2026-01-03"


def test_row_mapping_renders_null_optionals_as_empty() -> None:
    row = CreateCategoryRow(
        category_id=3,
        name="X",
        description=None,
        slug_category=None,
        image_category=None,
        created_at=CREATED,
        updated_at=UPDATED,
    )
    result = to_category_response(row)
    assert result.description == ""
    assert result.slug_category == ""
    assert result.image_category == ""


def test_row_mapping_delete_at_includes_deleted_at() -> None:
    result = to_category_response_delete_at(_active_row())
    assert result.id == 2
    assert result.deleted_at == "2026-02-01"


def test_row_mapping_delete_at_null_is_none() -> None:
    result = to_category_response_delete_at(_active_row(deleted_at=None))
    assert result.deleted_at is None


def test_row_mapping_accepts_category_and_by_id_shapes() -> None:
    by_id = GetCategoryByIDRow(
        category_id=4,
        name="D",
        description="d",
        slug_category="d",
        image_category="d.png",
        created_at=CREATED,
        updated_at=UPDATED,
    )
    category = Category(
        category_id=5,
        name="E",
        description="d",
        slug_category="e",
        image_category="e.png",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
    )
    assert to_category_response(by_id).id == 4
    assert to_category_response(category).id == 5


def _proto_category() -> category_common_pb2.CategoryResponse:
    message = category_common_pb2.ApiResponseCategory(status="success", message="ok")
    message.data.id = 7
    message.data.name = "Proto"
    message.data.description = "d"
    message.data.slug_category = "proto"
    message.data.image_category = "proto.png"
    message.data.created_at = "2026-05-06"
    message.data.updated_at = "2026-05-07"
    return message.data


def test_proto_mapping_passes_strings_through_unchanged() -> None:
    dumped = to_api_response_category(
        category_common_pb2.ApiResponseCategory(
            status="success", message="ok", data=_proto_category()
        )
    ).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "name": "Proto",
        "description": "d",
        "slug_category": "proto",
        "image_category": "proto.png",
        "created_at": "2026-05-06",
        "updated_at": "2026-05-07",
    }


def test_proto_mapping_uses_rest_field_id() -> None:
    mapped = map_category_response(_proto_category())
    assert mapped.id == 7


def test_proto_delete_at_missing_renders_empty_string() -> None:
    message = category_common_pb2.CategoryResponseDeleteAt(id=1)
    mapped = map_category_response_delete_at(message)
    assert mapped.deleted_at == ""


def test_proto_delete_at_present_passes_through() -> None:
    message = category_common_pb2.CategoryResponseDeleteAt(id=1)
    message.deleted_at.value = "2026-02-03"
    mapped = map_category_response_delete_at(message)
    assert mapped.deleted_at == "2026-02-03"


def test_pagination_mapping() -> None:
    message = category_common_pb2.ApiResponsePaginationCategory(
        status="success", message="ok"
    )
    message.data.add(id=1, name="A", created_at="2026-01-01")
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_category(message).model_dump()
    assert dumped["data"][0]["name"] == "A"
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_trashed_pagination_delete_at() -> None:
    message = category_common_pb2.ApiResponsePaginationCategoryDeleteAt(
        status="success", message="ok"
    )
    message.data.add(id=9, name="Trashed")
    message.data[0].deleted_at.value = "2026-02-03"
    dumped = to_api_response_pagination_category_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03"


def test_map_pagination_meta_none_defaults_to_zero() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


def test_stats_envelopes_map_lists() -> None:
    monthly = category_common_pb2.ApiResponseCategoryMonthlyTotalPrice(
        status="success", message="ok"
    )
    monthly.data.add(year="2026", month="01", total_revenue=1000)
    dumped_monthly = to_api_response_category_monthly_total_price(monthly).model_dump()
    assert dumped_monthly["data"][0] == {
        "year": "2026",
        "month": "01",
        "total_revenue": 1000,
    }

    yearly = category_common_pb2.ApiResponseCategoryYearlyTotalPrice(
        status="success", message="ok"
    )
    yearly.data.add(year="2026", total_revenue=5000)
    assert (
        to_api_response_category_yearly_total_price(yearly).model_dump()["data"][0][
            "total_revenue"
        ]
        == 5000
    )

    month_price = category_common_pb2.ApiResponseCategoryMonthPrice(
        status="success", message="ok"
    )
    month_price.data.add(
        month="01",
        category_id=1,
        category_name="E",
        order_count=2,
        items_sold=3,
        total_revenue=1000,
    )
    dumped_month_price = to_api_response_category_month_price(month_price).model_dump()
    assert dumped_month_price["data"][0]["category_name"] == "E"
    assert dumped_month_price["data"][0]["order_count"] == 2

    year_price = category_common_pb2.ApiResponseCategoryYearPrice(
        status="success", message="ok"
    )
    year_price.data.add(
        year="2026",
        category_id=1,
        category_name="E",
        order_count=2,
        items_sold=3,
        total_revenue=1000,
        unique_products_sold=1,
    )
    dumped_year_price = to_api_response_category_year_price(year_price).model_dump()
    assert dumped_year_price["data"][0]["unique_products_sold"] == 1
