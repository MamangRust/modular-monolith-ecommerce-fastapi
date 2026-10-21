"""Unit tests for the role response mapper."""

from __future__ import annotations

from pb.role import role_common_pb2
from shared.mapper.role import (
    map_pagination_meta,
    to_api_response_pagination_role,
    to_api_response_pagination_role_delete_at,
    to_api_response_role,
    to_api_response_role_all,
    to_api_response_role_delete,
    to_api_responses_role,
)


def _pagination() -> role_common_pb2.ApiResponsePaginationRole:
    message = role_common_pb2.ApiResponsePaginationRole(status="success", message="ok")
    message.data.add(id=1, name="Admin", created_at="2026-01-02", updated_at="2026-01-03")
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    return message


def test_pagination_mapping() -> None:
    result = to_api_response_pagination_role(_pagination())
    dumped = result.model_dump()
    assert dumped["status"] == "success"
    assert dumped["data"][0]["name"] == "Admin"
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_role_mapping_passes_timestamps_through_unchanged() -> None:
    message = role_common_pb2.ApiResponseRole(status="success", message="ok")
    message.data.id = 7
    message.data.name = "Role7"
    message.data.created_at = "2026-05-06"
    message.data.updated_at = "2026-05-07"
    dumped = to_api_response_role(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "name": "Role7",
        "created_at": "2026-05-06",
        "updated_at": "2026-05-07",
    }


def test_missing_deleted_at_renders_empty_string() -> None:
    message = role_common_pb2.ApiResponsePaginationRoleDeleteAt(
        status="success", message="ok"
    )
    row = message.data.add()
    row.id = 1
    row.name = "A"
    row.created_at = "2026-01-01"
    row.updated_at = "2026-01-02"
    dumped = to_api_response_pagination_role_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == ""


def test_present_deleted_at_is_passed_through() -> None:
    message = role_common_pb2.ApiResponsePaginationRoleDeleteAt(
        status="success", message="ok"
    )
    row = message.data.add()
    row.id = 1
    row.name = "A"
    row.created_at = "2026-01-01"
    row.updated_at = "2026-01-02"
    row.deleted_at.value = "2026-02-01"
    dumped = to_api_response_pagination_role_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-01"


def test_delete_and_all_responses_have_no_data() -> None:
    delete = role_common_pb2.ApiResponseRoleDelete(status="success", message="deleted")
    all_response = role_common_pb2.ApiResponseRoleAll(status="success", message="restored")
    assert to_api_response_role_delete(delete).model_dump()["data"] is None
    assert to_api_response_role_all(all_response).model_dump()["data"] is None


def test_multi_role_response() -> None:
    message = role_common_pb2.ApiResponsesRole(status="success", message="ok")
    message.data.add(id=1, name="A", created_at="2026-01-01", updated_at="2026-01-01")
    message.data.add(id=2, name="B", created_at="2026-01-02", updated_at="2026-01-02")
    dumped = to_api_responses_role(message).model_dump()
    assert [item["name"] for item in dumped["data"]] == ["A", "B"]


def test_map_pagination_meta_none_defaults_to_zero() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


def test_trashed_pagination_delete_at() -> None:
    message = role_common_pb2.ApiResponsePaginationRoleDeleteAt(status="success", message="ok")
    message.data.add(
        id=9, name="Trashed", created_at="2026-01-01", updated_at="2026-01-02"
    )
    message.data[0].deleted_at.value = "2026-02-03"
    dumped = to_api_response_pagination_role_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03"
