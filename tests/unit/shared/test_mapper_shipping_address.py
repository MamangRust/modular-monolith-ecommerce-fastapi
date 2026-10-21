"""Unit tests for the shipping address response mapper. Covers both input shapes: row dataclasses (which the mapper formats) and proto messages (which it passes through). The timestamp layout is date-only (`%Y-%m-%d`, like category), `shipping_cost` is truncated to an int, and the REST shape drops `courier`. The query and command delete-at mappers differ on an absent `deleted_at` wrapper (`None` vs `""`)."""

from __future__ import annotations

from datetime import datetime

from pb.shipping_address import shipping_address_common_pb2
from pkg.database.schema.shipping_address import (
    CreateShippingAddressRow,
    GetShippingAddressActiveRow,
    GetShippingAddressByOrderIDRow,
    GetShippingAddressRow,
    GetShippingByIDRow,
    ShippingAddress,
)
from shared.mapper.shipping_address import (
    map_pagination_meta,
    map_shipping_address_response,
    map_shipping_address_response_delete_at,
    to_api_response_pagination_shipping_address,
    to_api_response_pagination_shipping_address_delete_at,
    to_api_response_shipping_address,
    to_api_response_shipping_address_all,
    to_api_response_shipping_address_delete,
    to_api_response_shipping_address_delete_at,
    to_shipping_address_response,
    to_shipping_address_response_delete_at,
)

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 1, 10, 0, 0)


def _row() -> GetShippingAddressRow:
    return GetShippingAddressRow(
        shipping_address_id=1,
        order_id=10,
        alamat="Jl. Merdeka 1",
        provinsi="DKI Jakarta",
        negara="Indonesia",
        kota="Jakarta",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=12.75,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=1,
    )


def _active_row() -> GetShippingAddressActiveRow:
    return GetShippingAddressActiveRow(
        shipping_address_id=2,
        order_id=11,
        alamat="Jl. Merdeka 2",
        provinsi="Jawa Barat",
        negara="Indonesia",
        kota="Bandung",
        courier="SICEPAT",
        shipping_method="EXP",
        shipping_cost=20.5,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=DELETED,
        total_count=1,
    )


def test_row_mapping_formats_date_only_and_truncates_cost() -> None:
    result = to_shipping_address_response(_row())
    assert result.id == 1
    assert result.order_id == 10
    assert result.kota == "Jakarta"
    assert result.shipping_method == "REG"
    assert result.shipping_cost == 12
    assert result.created_at == "2026-01-02"
    assert result.updated_at == "2026-01-03"
    # The REST shape drops courier (ShippingAddressResponse has no field).
    assert not hasattr(result, "courier")


def test_row_mapping_delete_at_includes_deleted_at() -> None:
    result = to_shipping_address_response_delete_at(_active_row())
    assert result.id == 2
    assert result.shipping_cost == 20
    assert result.deleted_at == "2026-02-01"


def test_row_mapping_accepts_all_row_shapes() -> None:
    create_row = CreateShippingAddressRow(
        shipping_address_id=3,
        order_id=12,
        alamat="a",
        provinsi="p",
        negara="n",
        kota="k",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=5.0,
        created_at=CREATED,
        updated_at=UPDATED,
    )
    by_id = GetShippingByIDRow(
        shipping_address_id=4,
        order_id=13,
        alamat="a",
        provinsi="p",
        negara="n",
        kota="k",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=5.0,
        created_at=CREATED,
        updated_at=UPDATED,
    )
    by_order = GetShippingAddressByOrderIDRow(
        shipping_address_id=5,
        order_id=14,
        alamat="a",
        provinsi="p",
        negara="n",
        kota="k",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=5.0,
        created_at=CREATED,
        updated_at=UPDATED,
    )
    full = ShippingAddress(
        shipping_address_id=6,
        order_id=15,
        alamat="a",
        provinsi="p",
        negara="n",
        kota="k",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=5.0,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
    )
    assert to_shipping_address_response(create_row).id == 3
    assert to_shipping_address_response(by_id).order_id == 13
    assert to_shipping_address_response(by_order).kota == "k"
    # A restored row carries a None deleted_at, which formats to "".
    assert to_shipping_address_response_delete_at(full).deleted_at == ""


def _proto_shipping() -> shipping_address_common_pb2.ShippingResponse:
    return shipping_address_common_pb2.ShippingResponse(
        id=7,
        order_id=17,
        alamat="Jl. Sudirman 5",
        provinsi="DKI Jakarta",
        negara="Indonesia",
        kota="Jakarta",
        shippingMethod="JNE",
        shippingCost=15000,
        created_at="2026-05-06",
        updated_at="2026-05-07",
        courier="JNE",
    )


def test_proto_mapping_passes_strings_through_and_drops_courier() -> None:
    message = shipping_address_common_pb2.ApiResponseShipping(
        status="success", message="ok"
    )
    message.data.CopyFrom(_proto_shipping())
    dumped = to_api_response_shipping_address(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "order_id": 17,
        "alamat": "Jl. Sudirman 5",
        "provinsi": "DKI Jakarta",
        "negara": "Indonesia",
        "kota": "Jakarta",
        "shipping_method": "JNE",
        "shipping_cost": 15000,
        "created_at": "2026-05-06",
        "updated_at": "2026-05-07",
    }


def test_proto_delete_at_query_missing_renders_none() -> None:
    message = shipping_address_common_pb2.ShippingResponseDeleteAt(id=1)
    mapped = map_shipping_address_response_delete_at(message)
    assert mapped.deleted_at is None


def test_proto_delete_at_query_present_passes_through() -> None:
    message = shipping_address_common_pb2.ShippingResponseDeleteAt(id=1)
    message.deleted_at.value = "2026-02-03"
    mapped = map_shipping_address_response_delete_at(message)
    assert mapped.deleted_at == "2026-02-03"


def test_proto_delete_at_command_missing_renders_empty_string() -> None:
    message = shipping_address_common_pb2.ApiResponseShippingDeleteAt(
        status="success", message="ok"
    )
    message.data.id = 1
    dumped = to_api_response_shipping_address_delete_at(message).model_dump()
    assert dumped["data"]["deleted_at"] == ""


def test_proto_response_mapping_uses_rest_field_id() -> None:
    mapped = map_shipping_address_response(_proto_shipping())
    assert mapped.id == 7
    assert mapped.shipping_cost == 15000


def test_pagination_mapping() -> None:
    message = shipping_address_common_pb2.ApiResponsePaginationShipping(
        status="success", message="ok"
    )
    message.data.add(id=1, order_id=10, shippingMethod="REG", shippingCost=1000)
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_shipping_address(message).model_dump()
    assert dumped["data"][0]["order_id"] == 10
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_trashed_pagination_delete_at() -> None:
    message = shipping_address_common_pb2.ApiResponsePaginationShippingDeleteAt(
        status="success", message="ok"
    )
    message.data.add(id=9)
    message.data[0].deleted_at.value = "2026-02-03"
    dumped = to_api_response_pagination_shipping_address_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03"


def test_delete_envelope_has_no_data() -> None:
    message = shipping_address_common_pb2.ApiResponseShippingDelete(
        status="success", message="deleted"
    )
    dumped = to_api_response_shipping_address_delete(message).model_dump()
    assert dumped == {"status": "success", "message": "deleted", "data": None}


def test_all_envelope_has_no_data() -> None:
    message = shipping_address_common_pb2.ApiResponseShippingAll(
        status="success", message="restored"
    )
    dumped = to_api_response_shipping_address_all(message).model_dump()
    assert dumped == {"status": "success", "message": "restored", "data": None}


def test_map_pagination_meta_none_defaults() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0
