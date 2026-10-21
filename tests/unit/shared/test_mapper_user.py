"""Unit tests for the user response mapper."""

from __future__ import annotations

from pb.user import user_common_pb2
from shared.mapper.user import (
    map_pagination_meta,
    to_api_response_pagination_user,
    to_api_response_pagination_user_delete_at,
    to_api_response_user,
    to_api_response_user_all,
    to_api_response_user_delete,
    to_api_response_user_delete_at,
    to_api_responses_user,
)


def _pagination() -> user_common_pb2.ApiResponsePaginationUser:
    message = user_common_pb2.ApiResponsePaginationUser(status="success", message="ok")
    message.data.add(
        id=1,
        firstname="John",
        lastname="Doe",
        email="john@example.com",
        created_at="2026-01-02T10:00:00Z",
        updated_at="2026-01-03T10:00:00Z",
    )
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    return message


def test_pagination_mapping() -> None:
    dumped = to_api_response_pagination_user(_pagination()).model_dump()
    assert dumped["status"] == "success"
    assert dumped["data"][0]["firstname"] == "John"
    assert dumped["data"][0]["is_verified"] is False
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_user_mapping_passes_timestamps_through_unchanged() -> None:
    message = user_common_pb2.ApiResponseUser(status="success", message="ok")
    message.data.id = 7
    message.data.firstname = "Jane"
    message.data.lastname = "Roe"
    message.data.email = "jane@example.com"
    message.data.created_at = "2026-05-06T10:00:00Z"
    message.data.updated_at = "2026-05-07T10:00:00Z"
    dumped = to_api_response_user(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "firstname": "Jane",
        "lastname": "Roe",
        "email": "jane@example.com",
        "is_verified": False,
        "created_at": "2026-05-06T10:00:00Z",
        "updated_at": "2026-05-07T10:00:00Z",
    }


def test_missing_deleted_at_renders_none() -> None:
    """Deviation: emitted the zero time here; omits the wrapper."""
    message = user_common_pb2.ApiResponseUserDeleteAt(status="success", message="ok")
    message.data.id = 1
    message.data.firstname = "A"
    message.data.lastname = "B"
    message.data.email = "a@example.com"
    message.data.created_at = "2026-01-01T00:00:00Z"
    message.data.updated_at = "2026-01-02T00:00:00Z"
    dumped = to_api_response_user_delete_at(message).model_dump()
    assert dumped["data"]["deleted_at"] is None


def test_present_deleted_at_is_passed_through() -> None:
    message = user_common_pb2.ApiResponseUserDeleteAt(status="success", message="ok")
    message.data.id = 1
    message.data.firstname = "A"
    message.data.lastname = "B"
    message.data.email = "a@example.com"
    message.data.created_at = "2026-01-01T00:00:00Z"
    message.data.updated_at = "2026-01-02T00:00:00Z"
    message.data.deleted_at.value = "2026-02-01T00:00:00Z"
    dumped = to_api_response_user_delete_at(message).model_dump()
    assert dumped["data"]["deleted_at"] == "2026-02-01T00:00:00Z"


def test_delete_and_all_responses_have_no_data() -> None:
    delete = user_common_pb2.ApiResponseUserDelete(status="success", message="deleted")
    all_response = user_common_pb2.ApiResponseUserAll(status="success", message="restored")
    assert to_api_response_user_delete(delete).model_dump()["data"] is None
    assert to_api_response_user_all(all_response).model_dump()["data"] is None


def test_multi_user_response() -> None:
    message = user_common_pb2.ApiResponsesUser(status="success", message="ok")
    message.data.add(id=1, firstname="A", lastname="B", email="a@x.com")
    message.data.add(id=2, firstname="C", lastname="D", email="c@x.com")
    dumped = to_api_responses_user(message).model_dump()
    assert [item["firstname"] for item in dumped["data"]] == ["A", "C"]


def test_map_pagination_meta_none_defaults_to_zero() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


def test_trashed_pagination_delete_at() -> None:
    message = user_common_pb2.ApiResponsePaginationUserDeleteAt(
        status="success", message="ok"
    )
    message.data.add(
        id=9,
        firstname="Trashed",
        lastname="User",
        email="t@x.com",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-02T00:00:00Z",
    )
    message.data[0].deleted_at.value = "2026-02-03T00:00:00Z"
    dumped = to_api_response_pagination_user_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03T00:00:00Z"
