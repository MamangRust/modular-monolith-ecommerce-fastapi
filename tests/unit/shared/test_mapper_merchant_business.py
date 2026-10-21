"""Unit tests for the merchant_business REST mappers. The proto already carries formatted strings (`%Y-%m-%d %H:%M:%S.mmm`), so the mapper passes them through unchanged. Unlike merchant_award, the merchant_business mapper DOES copy `merchant_name` from the proto; the handler simply never fills it, so it is always `""` on the wire (tested here by feeding a proto with `merchant_name` set and confirming the mapper copies it). `deleted_at` renders `""` when no wrapper is attached and the wrapper value when present."""

from __future__ import annotations

from pb.merchant_business import merchant_business_common_pb2
from shared.mapper.merchant_business import (
    map_merchant_business_response,
    map_merchant_business_response_delete_at,
    map_pagination_meta,
    to_api_response_merchant_business,
    to_api_response_merchant_business_delete_at,
    to_api_response_pagination_merchant_business,
    to_api_response_pagination_merchant_business_delete_at,
    to_api_responses_merchant_business,
)


def _proto_business(**overrides):
    values = {
        "id": 7,
        "merchant_id": 20,
        "business_type": "Toko Elektronik",
        "tax_id": "01.234.567.8-999.000",
        "established_year": 2010,
        "number_of_employees": 15,
        "website_url": "https://technostore.com",
        "created_at": "2026-05-06 01:02:03.000",
        "updated_at": "2026-05-07 04:05:06.000",
        "merchant_name": "Elektronik Store",
    }
    values.update(overrides)
    return merchant_business_common_pb2.MerchantBusinessResponse(**values)


def test_business_proto_mapping_passes_strings_and_copies_merchant_name() -> None:
    message = merchant_business_common_pb2.ApiResponseMerchantBusiness(
        status="success", message="ok"
    )
    message.data.CopyFrom(_proto_business())
    dumped = to_api_response_merchant_business(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "merchant_id": 20,
        "business_type": "Toko Elektronik",
        "tax_id": "01.234.567.8-999.000",
        "established_year": 2010,
        "number_of_employees": 15,
        "website_url": "https://technostore.com",
        "created_at": "2026-05-06 01:02:03.000",
        "updated_at": "2026-05-07 04:05:06.000",
        "merchant_name": "Elektronik Store",
    }


def test_business_mapper_copies_merchant_name_when_present() -> None:
    # Unlike merchant_award, the mapper reads the proto `merchant_name`.
    assert map_merchant_business_response(_proto_business()).merchant_name == (
        "Elektronik Store"
    )
    # When the handler never fills it, it stays "" (zero value).
    assert map_merchant_business_response(_proto_business(merchant_name="")).merchant_name == ""


def test_business_delete_at_missing_renders_empty_and_present_passes_through() -> None:
    proto = merchant_business_common_pb2.MerchantBusinessResponseDeleteAt(
        id=1, merchant_id=2
    )
    assert map_merchant_business_response_delete_at(proto).deleted_at == ""

    proto.deleted_at.value = "2026-02-03 00:00:00.000"
    assert (
        map_merchant_business_response_delete_at(proto).deleted_at
        == "2026-02-03 00:00:00.000"
    )


def test_business_delete_at_api_response() -> None:
    message = merchant_business_common_pb2.ApiResponseMerchantBusinessDeleteAt(
        status="success", message="ok"
    )
    message.data.id = 3
    message.data.merchant_id = 2
    message.data.deleted_at.value = "2026-02-03 00:00:00.000"
    dumped = to_api_response_merchant_business_delete_at(message).model_dump()
    assert dumped["data"]["id"] == 3
    assert dumped["data"]["deleted_at"] == "2026-02-03 00:00:00.000"
    assert dumped["data"]["merchant_name"] == ""


def test_business_plain_list_api_response() -> None:
    message = merchant_business_common_pb2.ApiResponsesMerchantBusiness(
        status="success", message="ok"
    )
    message.data.add(id=1, merchant_id=2, business_type="A")
    message.data.add(id=2, merchant_id=2, business_type="B")
    dumped = to_api_responses_merchant_business(message).model_dump()
    assert [row["id"] for row in dumped["data"]] == [1, 2]


def test_business_pagination_mapping() -> None:
    message = merchant_business_common_pb2.ApiResponsePaginationMerchantBusiness(
        status="success", message="ok"
    )
    message.data.add(id=1, merchant_id=2, business_type="A")
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_merchant_business(message).model_dump()
    assert dumped["data"][0]["id"] == 1
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_business_trashed_pagination_delete_at() -> None:
    message = (
        merchant_business_common_pb2.ApiResponsePaginationMerchantBusinessDeleteAt(
            status="success", message="ok"
        )
    )
    message.data.add(id=9, merchant_id=2, business_type="A")
    message.data[0].deleted_at.value = "2026-02-03 00:00:00.000"
    dumped = to_api_response_pagination_merchant_business_delete_at(
        message
    ).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03 00:00:00.000"


def test_map_pagination_meta_none_defaults() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


__all__ = []
