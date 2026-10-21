"""Unit tests for the merchant_policy REST mappers. The proto already carries formatted strings (`%Y-%m-%d %H:%M:%S.mmm`), so the mapper passes them through unchanged. the merchant_policy mapper copies `merchant_name` from the proto (filled for list rows by the handler), so it is tested here by feeding a proto with `merchant_name` set. `deleted_at` renders `""` when no wrapper is attached and the wrapper value when present."""

from __future__ import annotations

from pb.merchant_policy import merchant_policy_common_pb2
from shared.mapper.merchant_policy import (
    map_merchant_policy_response,
    map_merchant_policy_response_delete_at,
    map_pagination_meta,
    to_api_response_merchant_policy,
    to_api_response_merchant_policy_delete_at,
    to_api_response_pagination_merchant_policies,
    to_api_response_pagination_merchant_policies_delete_at,
    to_api_responses_merchant_policies,
)


def _proto_policy(**overrides):
    values = {
        "id": 7,
        "merchant_id": 20,
        "policy_type": "Shipping",
        "title": "Free Shipping on Orders Above $50",
        "description": "desc",
        "created_at": "2026-05-06 01:02:03.000",
        "updated_at": "2026-05-07 04:05:06.000",
        "merchant_name": "Elektronik Store",
    }
    values.update(overrides)
    return merchant_policy_common_pb2.MerchantPoliciesResponse(**values)


def test_policy_proto_mapping_passes_strings_and_copies_merchant_name() -> None:
    message = merchant_policy_common_pb2.ApiResponseMerchantPolicies(
        status="success", message="ok"
    )
    message.data.CopyFrom(_proto_policy())
    dumped = to_api_response_merchant_policy(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "merchant_id": 20,
        "policy_type": "Shipping",
        "title": "Free Shipping on Orders Above $50",
        "description": "desc",
        "created_at": "2026-05-06 01:02:03.000",
        "updated_at": "2026-05-07 04:05:06.000",
        "merchant_name": "Elektronik Store",
    }


def test_policy_mapper_copies_merchant_name_when_present() -> None:
    assert map_merchant_policy_response(_proto_policy()).merchant_name == (
        "Elektronik Store"
    )
    assert (
        map_merchant_policy_response(_proto_policy(merchant_name="")).merchant_name
        == ""
    )


def test_policy_delete_at_missing_renders_empty_and_present_passes_through() -> None:
    proto = merchant_policy_common_pb2.MerchantPoliciesResponseDeleteAt(
        id=1, merchant_id=2
    )
    assert map_merchant_policy_response_delete_at(proto).deleted_at == ""

    proto.deleted_at.value = "2026-02-03 00:00:00.000"
    assert (
        map_merchant_policy_response_delete_at(proto).deleted_at
        == "2026-02-03 00:00:00.000"
    )


def test_policy_delete_at_api_response() -> None:
    message = merchant_policy_common_pb2.ApiResponseMerchantPoliciesDeleteAt(
        status="success", message="ok"
    )
    message.data.id = 3
    message.data.merchant_id = 2
    message.data.deleted_at.value = "2026-02-03 00:00:00.000"
    dumped = to_api_response_merchant_policy_delete_at(message).model_dump()
    assert dumped["data"]["id"] == 3
    assert dumped["data"]["deleted_at"] == "2026-02-03 00:00:00.000"
    assert dumped["data"]["merchant_name"] == ""


def test_policy_plain_list_api_response() -> None:
    message = merchant_policy_common_pb2.ApiResponsesMerchantPolicies(
        status="success", message="ok"
    )
    message.data.add(id=1, merchant_id=2, policy_type="A")
    message.data.add(id=2, merchant_id=2, policy_type="B")
    dumped = to_api_responses_merchant_policies(message).model_dump()
    assert [row["id"] for row in dumped["data"]] == [1, 2]


def test_policy_pagination_mapping() -> None:
    message = merchant_policy_common_pb2.ApiResponsePaginationMerchantPolicies(
        status="success", message="ok"
    )
    message.data.add(id=1, merchant_id=2, policy_type="A")
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_merchant_policies(message).model_dump()
    assert dumped["data"][0]["id"] == 1
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_policy_trashed_pagination_delete_at() -> None:
    message = (
        merchant_policy_common_pb2.ApiResponsePaginationMerchantPoliciesDeleteAt(
            status="success", message="ok"
        )
    )
    message.data.add(id=9, merchant_id=2, policy_type="A")
    message.data[0].deleted_at.value = "2026-02-03 00:00:00.000"
    dumped = to_api_response_pagination_merchant_policies_delete_at(
        message
    ).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03 00:00:00.000"


def test_map_pagination_meta_none_defaults() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


__all__ = []
