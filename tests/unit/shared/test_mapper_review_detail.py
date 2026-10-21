"""Unit tests for the review detail response mapper. Covers both input shapes: row dataclasses (formatted to date-only strings) and proto messages (passed through). The REST shape carries `id` (not `review_detail_id`), date-only timestamps, and a nullable `caption`. An absent `deleted_at` wrapper renders as `None` (the review_detail command mapper only attaches it when set, unlike the slider port which always sets it)."""

from __future__ import annotations

from datetime import datetime

from pb.review import review_common_pb2
from pb.review_detail import review_detail_common_pb2
from pkg.database.schema.review_detail import (
    CreateReviewDetailRow,
    GetReviewDetailByIDRow,
    GetReviewDetailsActiveRow,
    GetReviewDetailsRow,
    ReviewDetail,
)
from shared.mapper.review_detail import (
    map_pagination_meta,
    map_review_detail_response,
    map_review_detail_response_delete_at,
    to_api_response_pagination_review_detail,
    to_api_response_pagination_review_detail_delete_at,
    to_api_response_review_detail,
    to_api_response_review_detail_all,
    to_api_response_review_detail_delete,
    to_api_response_review_detail_delete_at,
    to_review_detail_response,
    to_review_detail_response_delete_at,
)

CREATED = datetime(2026, 1, 2)
UPDATED = datetime(2026, 1, 3)
DELETED = datetime(2026, 2, 1)


def _row(review_detail_id: int = 1, total: int = 1) -> GetReviewDetailsRow:
    return GetReviewDetailsRow(
        review_detail_id=review_detail_id,
        review_id=10,
        type="photo",
        url="/img/a.png",
        caption="Nice",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row() -> GetReviewDetailsActiveRow:
    return GetReviewDetailsActiveRow(
        review_detail_id=2,
        review_id=11,
        type="video",
        url="/img/b.png",
        caption="Bad",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=DELETED,
        total_count=1,
    )


def test_row_mapping_formats_date_only() -> None:
    result = to_review_detail_response(_row())
    assert result.id == 1
    assert result.review_id == 10
    assert result.type == "photo"
    assert result.url == "/img/a.png"
    assert result.caption == "Nice"
    assert result.created_at == "2026-01-02"
    assert result.updated_at == "2026-01-03"


def test_row_mapping_delete_at_includes_deleted_at() -> None:
    result = to_review_detail_response_delete_at(_active_row())
    assert result.id == 2
    assert result.type == "video"
    assert result.deleted_at == "2026-02-01"


def test_row_mapping_accepts_all_row_shapes() -> None:
    create_row = CreateReviewDetailRow(
        review_detail_id=3,
        review_id=12,
        type="photo",
        url="/c.png",
        caption=None,
        created_at=CREATED,
        updated_at=UPDATED,
    )
    by_id = GetReviewDetailByIDRow(
        review_detail_id=4,
        review_id=13,
        type="video",
        url="/d.png",
        caption="x",
        created_at=CREATED,
        updated_at=UPDATED,
    )
    full = ReviewDetail(
        review_detail_id=6,
        review_id=14,
        type="photo",
        url="/f.png",
        caption=None,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
    )
    assert to_review_detail_response(create_row).id == 3
    assert to_review_detail_response(by_id).caption == "x"
    # A restored row carries a None deleted_at; the row mapper keeps it None.
    assert to_review_detail_response_delete_at(full).deleted_at is None


def _proto_review_detail() -> review_detail_common_pb2.ReviewDetailsResponse:
    return review_detail_common_pb2.ReviewDetailsResponse(
        id=7,
        review_id=20,
        type="photo",
        url="/img/a.png",
        caption="cap",
        created_at="2026-05-06",
        updated_at="2026-05-07",
    )


def test_proto_mapping_passes_strings_through() -> None:
    message = review_detail_common_pb2.ApiResponseReviewDetail(
        status="success", message="ok"
    )
    message.data.CopyFrom(_proto_review_detail())
    dumped = to_api_response_review_detail(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "review_id": 20,
        "type": "photo",
        "url": "/img/a.png",
        "caption": "cap",
        "created_at": "2026-05-06",
        "updated_at": "2026-05-07",
    }


def test_proto_delete_at_missing_renders_none() -> None:
    message = review_detail_common_pb2.ReviewDetailsResponseDeleteAt()
    mapped = map_review_detail_response_delete_at(message)
    assert mapped.deleted_at is None


def test_proto_delete_at_present_passes_through() -> None:
    message = review_detail_common_pb2.ReviewDetailsResponseDeleteAt()
    message.deleted_at.value = "2026-02-03"
    mapped = map_review_detail_response_delete_at(message)
    assert mapped.deleted_at == "2026-02-03"


def test_proto_response_mapping_uses_rest_field_id() -> None:
    mapped = map_review_detail_response(_proto_review_detail())
    assert mapped.id == 7
    assert mapped.url == "/img/a.png"


def test_pagination_mapping() -> None:
    message = review_detail_common_pb2.ApiResponsePaginationReviewDetails(
        status="success", message="ok"
    )
    message.data.add(
        id=1, review_id=20, type="photo", url="/a.png", caption="cap"
    )
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_review_detail(message).model_dump()
    assert dumped["data"][0]["type"] == "photo"
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_trashed_pagination_delete_at() -> None:
    message = review_detail_common_pb2.ApiResponsePaginationReviewDetailsDeleteAt(
        status="success", message="ok"
    )
    message.data.add(
        id=9, review_id=20, type="video", url="/a.png", caption="cap"
    )
    message.data[0].deleted_at.value = "2026-02-03"
    dumped = to_api_response_pagination_review_detail_delete_at(
        message
    ).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03"


def test_delete_envelope_has_no_data() -> None:
    message = review_common_pb2.ApiResponseReviewDelete(
        status="success", message="deleted"
    )
    dumped = to_api_response_review_detail_delete(message).model_dump()
    assert dumped == {"status": "success", "message": "deleted", "data": None}


def test_all_envelope_has_no_data() -> None:
    message = review_common_pb2.ApiResponseReviewAll(
        status="success", message="restored"
    )
    dumped = to_api_response_review_detail_all(message).model_dump()
    assert dumped == {"status": "success", "message": "restored", "data": None}


def test_command_delete_at_envelope() -> None:
    message = review_detail_common_pb2.ApiResponseReviewDetailDeleteAt(
        status="success", message="ok"
    )
    message.data.id = 1
    message.data.type = "photo"
    message.data.url = "/a.png"
    dumped = to_api_response_review_detail_delete_at(message).model_dump()
    assert dumped["data"]["id"] == 1
    # Absent wrapper renders as None (not "").
    assert dumped["data"]["deleted_at"] is None


def test_map_pagination_meta_none_defaults() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


__all__ = []
