"""Unit tests for the merchant_award REST mappers. The proto already carries formatted strings (dates `%Y-%m-%d`, timestamps `%Y-%m-%d %H:%M:%S.mmm`), so the mapper passes them through unchanged. `merchant_name` is never copied (leaves it at the zero value -> `""`). `deleted_at` renders `""` when no wrapper is attached and the wrapper value when present."""

from __future__ import annotations

from pb.merchant_award import merchant_award_common_pb2
from shared.mapper.merchant_award import (
    map_merchant_award_response,
    map_merchant_award_response_delete_at,
    map_pagination_meta,
    to_api_response_merchant_award,
    to_api_response_merchant_award_delete_at,
    to_api_response_pagination_merchant_award,
    to_api_response_pagination_merchant_award_delete_at,
    to_api_responses_merchant_award,
)


def _proto_award(**overrides):
    values = {
        "id": 7,
        "merchant_id": 20,
        "title": "ISO 9001",
        "description": "Quality management",
        "issued_by": "BSN",
        "issue_date": "2026-01-02",
        "expiry_date": "2027-01-02",
        "certificate_url": "https://certs.example.com/1",
        "created_at": "2026-05-06 01:02:03.000",
        "updated_at": "2026-05-07 04:05:06.000",
        "merchant_name": "Elektronik Store",
    }
    values.update(overrides)
    return merchant_award_common_pb2.MerchantAwardResponse(**values)


def test_award_proto_mapping_passes_strings_and_drops_merchant_name() -> None:
    message = merchant_award_common_pb2.ApiResponseMerchantAward(
        status="success", message="ok"
    )
    message.data.CopyFrom(_proto_award())
    dumped = to_api_response_merchant_award(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "merchant_id": 20,
        "title": "ISO 9001",
        "description": "Quality management",
        "issued_by": "BSN",
        "issue_date": "2026-01-02",
        "expiry_date": "2027-01-02",
        "certificate_url": "https://certs.example.com/1",
        "created_at": "2026-05-06 01:02:03.000",
        "updated_at": "2026-05-07 04:05:06.000",
        "merchant_name": "",
    }


def test_award_plain_mapper_never_copies_merchant_name() -> None:
    # never reads the proto `merchant_name`.
    assert map_merchant_award_response(_proto_award()).merchant_name == ""


def test_award_delete_at_missing_renders_empty_and_present_passes_through() -> None:
    proto = merchant_award_common_pb2.MerchantAwardResponseDeleteAt(
        id=1, merchant_id=2
    )
    assert map_merchant_award_response_delete_at(proto).deleted_at == ""

    proto.deleted_at.value = "2026-02-03 00:00:00.000"
    assert (
        map_merchant_award_response_delete_at(proto).deleted_at
        == "2026-02-03 00:00:00.000"
    )


def test_award_delete_at_api_response() -> None:
    message = merchant_award_common_pb2.ApiResponseMerchantAwardDeleteAt(
        status="success", message="ok"
    )
    message.data.id = 3
    message.data.merchant_id = 2
    message.data.deleted_at.value = "2026-02-03 00:00:00.000"
    dumped = to_api_response_merchant_award_delete_at(message).model_dump()
    assert dumped["data"]["id"] == 3
    assert dumped["data"]["deleted_at"] == "2026-02-03 00:00:00.000"
    assert dumped["data"]["merchant_name"] == ""


def test_award_plain_list_api_response() -> None:
    message = merchant_award_common_pb2.ApiResponsesMerchantAward(
        status="success", message="ok"
    )
    message.data.add(id=1, merchant_id=2, title="A")
    message.data.add(id=2, merchant_id=2, title="B")
    dumped = to_api_responses_merchant_award(message).model_dump()
    assert [row["id"] for row in dumped["data"]] == [1, 2]


def test_award_pagination_mapping() -> None:
    message = merchant_award_common_pb2.ApiResponsePaginationMerchantAward(
        status="success", message="ok"
    )
    message.data.add(id=1, merchant_id=2, title="A")
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_merchant_award(message).model_dump()
    assert dumped["data"][0]["id"] == 1
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_award_trashed_pagination_delete_at() -> None:
    message = merchant_award_common_pb2.ApiResponsePaginationMerchantAwardDeleteAt(
        status="success", message="ok"
    )
    message.data.add(id=9, merchant_id=2, title="A")
    message.data[0].deleted_at.value = "2026-02-03 00:00:00.000"
    dumped = to_api_response_pagination_merchant_award_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03 00:00:00.000"


def test_map_pagination_meta_none_defaults() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


__all__ = []
