"""Unit tests for the review REST mappers. The proto already carries formatted strings, so the mappers pass them through. The review-specific points: - `ReviewResponseDeleteAt` keeps `""` when the proto `StringValue` wrapper is present (the handler always sets it) and `None` when absent; - `ReviewsDetailResponse` keeps `deleted_at=None` unless the plain string is non-empty; the nested `ReviewDetailResponse.updated_at` is always `""`; - `ToApiResponsePaginationReviewsDetail` drops the pagination block (zero meta), reproducing mapper."""

from __future__ import annotations

from pb.review import review_common_pb2
from shared.mapper.review import (
    map_pagination_meta,
    map_review_detail_response,
    map_review_response,
    map_review_response_delete_at,
    map_reviews_detail_response,
    to_api_response_pagination_review,
    to_api_response_pagination_review_delete_at,
    to_api_response_pagination_reviews_detail,
    to_api_response_review,
    to_api_response_review_all,
    to_api_response_review_delete,
    to_api_response_review_delete_at,
    to_api_responses_reviews,
)


def _proto_review(**overrides):
    values = {
        "id": 7,
        "user_id": 5,
        "product_id": 10,
        "name": "John",
        "comment": "Produk bagus!",
        "rating": 5,
        "created_at": "2026-05-06",
        "updated_at": "2026-05-07",
    }
    values.update(overrides)
    return review_common_pb2.ReviewResponse(**values)


def _proto_delete_at(**overrides):
    values = {
        "id": 7,
        "user_id": 5,
        "product_id": 10,
        "name": "John",
        "comment": "Produk bagus!",
        "rating": 5,
        "created_at": "2026-05-06",
        "updated_at": "2026-05-07",
    }
    values.update(overrides)
    return review_common_pb2.ReviewResponseDeleteAt(**values)


def test_review_plain_mapping_passes_strings_through() -> None:
    message = review_common_pb2.ApiResponseReview(status="success", message="ok")
    message.data.CopyFrom(_proto_review())
    dumped = to_api_response_review(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "user_id": 5,
        "product_id": 10,
        "name": "John",
        "comment": "Produk bagus!",
        "rating": 5,
        "created_at": "2026-05-06",
        "updated_at": "2026-05-07",
    }


def test_review_plain_list_api_response() -> None:
    message = review_common_pb2.ApiResponsesReview(status="success", message="ok")
    message.data.add(id=1, name="A")
    message.data.add(id=2, name="B")
    dumped = to_api_responses_reviews(message).model_dump()
    assert [row["id"] for row in dumped["data"]] == [1, 2]


def test_review_pagination_mapping() -> None:
    message = review_common_pb2.ApiResponsePaginationReview(
        status="success", message="ok"
    )
    message.data.add(id=1, name="A")
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_review(message).model_dump()
    assert dumped["data"][0]["id"] == 1
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_review_detail_pagination_drops_pagination_block() -> None:
    message = review_common_pb2.ApiResponsePaginationReviewDetail(
        status="success", message="ok"
    )
    message.data.add(id=1, name="A")
    message.pagination.current_page = 2
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_reviews_detail(message).model_dump()
    # never sets the pagination block here (zero-valued struct -> all zeros).
    assert dumped["pagination"] == {
        "current_page": 0,
        "page_size": 0,
        "total_pages": 0,
        "total_records": 0,
    }


def test_review_delete_at_pagination_mapping() -> None:
    message = review_common_pb2.ApiResponsePaginationReviewDeleteAt(
        status="success", message="ok"
    )
    message.data.add(id=1, name="A")
    message.data[0].deleted_at.value = "2026-05-08"
    message.pagination.total_records = 3
    dumped = to_api_response_pagination_review_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-05-08"
    assert dumped["pagination"]["total_records"] == 3


def test_review_delete_at_wrapper_present_vs_absent() -> None:
    present = _proto_delete_at()
    present.deleted_at.value = ""  # wrapper present, empty value
    assert map_review_response_delete_at(present).deleted_at == ""

    absent = _proto_delete_at()
    assert map_review_response_delete_at(absent).deleted_at is None


def test_reviews_detail_nested_and_deleted_at() -> None:
    proto = review_common_pb2.ReviewsDetailResponse(
        id=1, name="A", created_at="2026-01-02 03:04:05.000"
    )
    mapped = map_reviews_detail_response(proto)
    assert mapped.review_detail is None
    assert mapped.deleted_at is None

    proto.review_detail.id = 9
    proto.review_detail.type = "photo"
    proto.review_detail.caption = "cap"
    proto.deleted_at = "2026-02-01 06:07:08.000"
    mapped = map_reviews_detail_response(proto)
    assert mapped.review_detail is not None
    assert mapped.review_detail.id == 9
    assert mapped.review_detail.updated_at == ""
    assert mapped.deleted_at == "2026-02-01 06:07:08.000"


def test_review_detail_response_updated_at_is_empty() -> None:
    proto = review_common_pb2.ReviewDetailResponse(id=9, type="photo")
    mapped = map_review_detail_response(proto)
    assert mapped.updated_at == ""


def test_review_command_delete_and_all_envelopes() -> None:
    message = review_common_pb2.ApiResponseReviewDeleteAt(
        status="success", message="ok"
    )
    message.data.CopyFrom(_proto_delete_at())
    assert to_api_response_review_delete_at(message).data is not None

    deleted = review_common_pb2.ApiResponseReviewDelete(
        status="success", message="Successfully deleted review permanently"
    )
    assert to_api_response_review_delete(deleted).model_dump()["data"] is None

    all_message = review_common_pb2.ApiResponseReviewAll(
        status="success", message="Successfully restored all reviews"
    )
    assert to_api_response_review_all(all_message).message == (
        "Successfully restored all reviews"
    )


def test_map_pagination_meta_none_defaults() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


def test_map_review_response_uses_defaults_for_zero_values() -> None:
    mapped = map_review_response(review_common_pb2.ReviewResponse(id=1))
    assert mapped.user_id == 0
    assert mapped.name == ""
    assert mapped.comment == ""


__all__ = []
