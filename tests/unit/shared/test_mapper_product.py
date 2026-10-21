"""Unit tests for the product REST mappers.

The proto already carries formatted strings (`%Y-%m-%d %H:%M:%S.mmm`), so the
mapper passes them through unchanged. `rating` is widened from the proto float;
`deleted_at` renders `""` when no wrapper is attached (port convention) and the
wrapper value when present.
"""

from __future__ import annotations

from pb.product import product_common_pb2
from shared.mapper.product import (
    map_pagination_meta,
    map_product_response,
    map_product_response_delete_at,
    to_api_response_pagination_product,
    to_api_response_pagination_product_delete_at,
    to_api_response_product,
    to_api_response_product_all,
    to_api_response_product_delete,
    to_api_response_product_delete_at,
    to_api_responses_products,
)


def _proto_product(**overrides):
    values = {
        "id": 7,
        "merchant_id": 20,
        "category_id": 3,
        "name": "Galaxy S24",
        "description": "desc",
        "price": 1200,
        "count_in_stock": 5,
        "brand": "Samsung",
        "weight": 200,
        "rating": 4.5,
        "slug_product": "galaxy-s24",
        "image_product": "uploads/products/galaxy-s24.jpg",
        "created_at": "2026-05-06 01:02:03.000",
        "updated_at": "2026-05-07 04:05:06.000",
    }
    values.update(overrides)
    return product_common_pb2.ProductResponse(**values)


def test_product_proto_mapping_passes_strings_and_widens_rating() -> None:
    message = product_common_pb2.ApiResponseProduct(status="success", message="ok")
    message.data.CopyFrom(_proto_product())
    dumped = to_api_response_product(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "merchant_id": 20,
        "category_id": 3,
        "name": "Galaxy S24",
        "description": "desc",
        "price": 1200,
        "count_in_stock": 5,
        "brand": "Samsung",
        "weight": 200,
        "rating": 4.5,
        "slug_product": "galaxy-s24",
        "image_product": "uploads/products/galaxy-s24.jpg",
        "created_at": "2026-05-06 01:02:03.000",
        "updated_at": "2026-05-07 04:05:06.000",
    }


def test_product_delete_at_missing_renders_empty_and_present_passes_through() -> None:
    proto = product_common_pb2.ProductResponseDeleteAt(id=1, merchant_id=2)
    assert map_product_response_delete_at(proto).deleted_at == ""

    proto.deleted_at.value = "2026-02-03 00:00:00.000"
    assert (
        map_product_response_delete_at(proto).deleted_at == "2026-02-03 00:00:00.000"
    )


def test_product_delete_at_api_response() -> None:
    message = product_common_pb2.ApiResponseProductDeleteAt(
        status="success", message="ok"
    )
    message.data.id = 3
    message.data.merchant_id = 2
    message.data.deleted_at.value = "2026-02-03 00:00:00.000"
    dumped = to_api_response_product_delete_at(message).model_dump()
    assert dumped["data"]["id"] == 3
    assert dumped["data"]["deleted_at"] == "2026-02-03 00:00:00.000"


def test_product_plain_list_api_response() -> None:
    message = product_common_pb2.ApiResponsesProduct(status="success", message="ok")
    message.data.add(id=1, merchant_id=2, name="A")
    message.data.add(id=2, merchant_id=2, name="B")
    dumped = to_api_responses_products(message).model_dump()
    assert [row["id"] for row in dumped["data"]] == [1, 2]


def test_product_pagination_mapping() -> None:
    message = product_common_pb2.ApiResponsePaginationProduct(
        status="success", message="ok"
    )
    message.data.add(id=1, merchant_id=2, name="A")
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_product(message).model_dump()
    assert dumped["data"][0]["id"] == 1
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_product_trashed_pagination_delete_at() -> None:
    message = product_common_pb2.ApiResponsePaginationProductDeleteAt(
        status="success", message="ok"
    )
    message.data.add(id=9, merchant_id=2, name="A")
    message.data[0].deleted_at.value = "2026-02-03 00:00:00.000"
    dumped = to_api_response_pagination_product_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03 00:00:00.000"


def test_product_delete_and_all_envelopes() -> None:
    deleted = product_common_pb2.ApiResponseProductDelete(
        status="success", message="Successfully deleted product permanently"
    )
    assert to_api_response_product_delete(deleted).model_dump()["data"] is None

    all_message = product_common_pb2.ApiResponseProductAll(
        status="success", message="Successfully restored all products"
    )
    assert to_api_response_product_all(all_message).message == (
        "Successfully restored all products"
    )


def test_map_pagination_meta_none_defaults() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


def test_map_product_response_uses_defaults_for_zero_values() -> None:
    proto = product_common_pb2.ProductResponse(id=1)
    mapped = map_product_response(proto)
    assert mapped.merchant_id == 0
    assert mapped.rating == 0.0
    assert mapped.name == ""


__all__ = []
