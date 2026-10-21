"""Unit tests for the merchant/document response mapper. Covers both input shapes: row dataclasses (formatted `%Y-%m-%d %H:%M:%S`,) and proto messages (already-formatted strings, passed through). Merchant REST uses `id` directly; the document REST `id` comes from proto `document_id`, and the document REST `created_at` is filled from the proto `uploaded_at` (the DB `uploaded_at` column never reaches the wire). `deleted_at` on the row side is always attached, so a live row renders as `""` (a NULL value); the proto side renders an absent wrapper as `""` too, matching the mapper that always sets the pointer."""

from __future__ import annotations

from datetime import datetime

from pb.merchant import merchant_common_pb2
from pb.merchant_document import merchant_document_common_pb2
from pkg.database.schema.merchant import (
    CreateMerchantRow,
    GetMerchantsActiveRow,
    GetMerchantsRow,
    Merchant,
)
from pkg.database.schema.merchant_document import (
    CreateMerchantDocumentRow,
    GetActiveMerchantDocumentsRow,
    GetMerchantDocumentsRow,
    MerchantDocument,
)
from shared.mapper.merchant import (
    map_merchant_response_delete_at,
    map_pagination_meta,
    to_api_response_merchant,
    to_api_response_merchant_all,
    to_api_response_merchant_delete,
    to_api_response_merchant_document,
    to_api_response_merchant_document_all,
    to_api_response_merchant_document_delete,
    to_api_response_pagination_merchant,
    to_api_response_pagination_merchant_delete_at,
    to_api_response_pagination_merchant_document,
    to_api_response_pagination_merchant_document_delete_at,
    to_merchant_document_response,
    to_merchant_document_response_delete_at,
    to_merchant_response,
    to_merchant_response_delete_at,
)

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 1, 5, 6, 7)


def _row(merchant_id: int = 1, total: int = 1) -> GetMerchantsRow:
    return GetMerchantsRow(
        merchant_id=merchant_id,
        user_id=10,
        name="Elektronik Store",
        description="desc",
        address="addr",
        contact_email="a@b.com",
        contact_phone="0812",
        status="active",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row() -> GetMerchantsActiveRow:
    return GetMerchantsActiveRow(
        merchant_id=2,
        user_id=11,
        name="Rumah Indah",
        description=None,
        address=None,
        contact_email=None,
        contact_phone=None,
        status="active",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=DELETED,
        total_count=1,
    )


def test_merchant_row_formats_timestamps_and_collapses_nulls() -> None:
    result = to_merchant_response(_row())
    assert result.id == 1
    assert result.user_id == 10
    assert result.name == "Elektronik Store"
    assert result.created_at == "2026-01-02 03:04:05"
    assert result.updated_at == "2026-01-03 04:05:06"


def test_merchant_row_null_strings_become_empty() -> None:
    row = CreateMerchantRow(
        merchant_id=2,
        user_id=11,
        name="Rumah Indah",
        description=None,
        address=None,
        contact_email=None,
        contact_phone=None,
        status="active",
        created_at=CREATED,
        updated_at=UPDATED,
    )
    result = to_merchant_response(row)
    assert result.description == ""
    assert result.address == ""
    assert result.contact_email == ""
    assert result.contact_phone == ""


def test_merchant_delete_at_row_live_row_renders_empty_deleted_at() -> None:
    live = Merchant(
        merchant_id=3,
        user_id=12,
        name="N",
        description=None,
        address=None,
        contact_email=None,
        contact_phone=None,
        status="active",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
    )
    assert to_merchant_response_delete_at(live).deleted_at == ""
    assert to_merchant_response_delete_at(_active_row()).deleted_at == (
        "2026-02-01 05:06:07"
    )


def test_merchant_row_accepts_create_row_shape() -> None:
    row = CreateMerchantRow(
        merchant_id=4,
        user_id=13,
        name="X",
        description=None,
        address=None,
        contact_email=None,
        contact_phone=None,
        status="active",
        created_at=CREATED,
        updated_at=UPDATED,
    )
    assert to_merchant_response(row).id == 4


def _proto_merchant() -> merchant_common_pb2.MerchantResponse:
    return merchant_common_pb2.MerchantResponse(
        id=7,
        user_id=20,
        name="Sport Zone",
        description="d",
        address="a",
        contact_email="e@f.com",
        contact_phone="0899",
        status="active",
        created_at="2026-05-06 01:02:03",
        updated_at="2026-05-07 04:05:06",
    )


def test_merchant_proto_mapping_passes_strings_through() -> None:
    message = merchant_common_pb2.ApiResponseMerchant(status="success", message="ok")
    message.data.CopyFrom(_proto_merchant())
    dumped = to_api_response_merchant(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "user_id": 20,
        "name": "Sport Zone",
        "description": "d",
        "address": "a",
        "contact_email": "e@f.com",
        "contact_phone": "0899",
        "status": "active",
        "created_at": "2026-05-06 01:02:03",
        "updated_at": "2026-05-07 04:05:06",
    }


def test_merchant_proto_delete_at_missing_renders_empty() -> None:
    message = merchant_common_pb2.MerchantResponseDeleteAt(id=1, user_id=2, name="N")
    mapped = map_merchant_response_delete_at(message)
    assert mapped.deleted_at == ""


def test_merchant_proto_delete_at_present_passes_through() -> None:
    message = merchant_common_pb2.MerchantResponseDeleteAt(id=1, user_id=2, name="N")
    message.deleted_at.value = "2026-02-03 00:00:00"
    mapped = map_merchant_response_delete_at(message)
    assert mapped.deleted_at == "2026-02-03 00:00:00"


def test_merchant_pagination_mapping() -> None:
    message = merchant_common_pb2.ApiResponsePaginationMerchant(
        status="success", message="ok"
    )
    message.data.add(id=1, user_id=2, name="N")
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_merchant(message).model_dump()
    assert dumped["data"][0]["id"] == 1
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_merchant_trashed_pagination_delete_at() -> None:
    message = merchant_common_pb2.ApiResponsePaginationMerchantDeleteAt(
        status="success", message="ok"
    )
    message.data.add(id=9, user_id=2, name="N")
    message.data[0].deleted_at.value = "2026-02-03 00:00:00"
    dumped = to_api_response_pagination_merchant_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03 00:00:00"


def test_merchant_delete_and_all_envelopes_have_no_data() -> None:
    deleted = merchant_common_pb2.ApiResponseMerchantDelete(
        status="success", message="deleted"
    )
    all_message = merchant_common_pb2.ApiResponseMerchantAll(
        status="success", message="restored"
    )
    assert to_api_response_merchant_delete(deleted).model_dump() == {
        "status": "success",
        "message": "deleted",
        "data": None,
    }
    assert to_api_response_merchant_all(all_message).model_dump() == {
        "status": "success",
        "message": "restored",
        "data": None,
    }


# ---- documents ----


def _doc_row(document_id: int = 1, total: int = 1) -> GetMerchantDocumentsRow:
    return GetMerchantDocumentsRow(
        document_id=document_id,
        merchant_id=10,
        document_type="NIB",
        document_url="uploads/merchant_document/a.pdf",
        status="pending",
        note=None,
        uploaded_at=CREATED,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _doc_active_row() -> GetActiveMerchantDocumentsRow:
    return GetActiveMerchantDocumentsRow(
        document_id=2,
        merchant_id=11,
        document_type="SIUP",
        document_url="uploads/merchant_document/b.pdf",
        status="approved",
        note="ok",
        uploaded_at=CREATED,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=DELETED,
        total_count=1,
    )


def test_document_row_uses_created_at_and_collapses_null_note() -> None:
    result = to_merchant_document_response(_doc_row())
    assert result.id == 1
    assert result.merchant_id == 10
    assert result.document_type == "NIB"
    assert result.note == ""
    assert result.created_at == "2026-01-02 03:04:05"
    assert result.updated_at == "2026-01-03 04:05:06"


def test_document_delete_at_row() -> None:
    assert to_merchant_document_response_delete_at(_doc_active_row()).deleted_at == (
        "2026-02-01 05:06:07"
    )
    live = MerchantDocument(
        document_id=3,
        merchant_id=12,
        document_type="NIB",
        document_url="u",
        status="pending",
        note=None,
        uploaded_at=CREATED,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
    )
    assert to_merchant_document_response_delete_at(live).deleted_at == ""


def test_document_row_accepts_create_row_shape() -> None:
    row = CreateMerchantDocumentRow(
        document_id=5,
        merchant_id=13,
        document_type="NIB",
        document_url="u",
        status="pending",
        note=None,
        uploaded_at=CREATED,
        created_at=CREATED,
        updated_at=UPDATED,
    )
    assert to_merchant_document_response(row).id == 5


def _proto_document() -> merchant_document_common_pb2.MerchantDocument:
    return merchant_document_common_pb2.MerchantDocument(
        document_id=7,
        merchant_id=20,
        document_type="NIB",
        document_url="uploads/a.pdf",
        status="approved",
        note="ok",
        uploaded_at="2026-05-06 01:02:03",
        updated_at="2026-05-07 04:05:06",
    )


def test_document_proto_mapping_translates_document_id_and_uploaded_at() -> None:
    message = merchant_document_common_pb2.ApiResponseMerchantDocument(
        status="success", message="ok"
    )
    message.data.CopyFrom(_proto_document())
    dumped = to_api_response_merchant_document(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "merchant_id": 20,
        "document_type": "NIB",
        "document_url": "uploads/a.pdf",
        "status": "approved",
        "note": "ok",
        "created_at": "2026-05-06 01:02:03",
        "updated_at": "2026-05-07 04:05:06",
    }


def test_document_pagination_mapping() -> None:
    message = merchant_document_common_pb2.ApiResponsePaginationMerchantDocument(
        status="success", message="ok"
    )
    message.data.add(document_id=1, merchant_id=2, document_type="NIB")
    message.pagination.current_page = 1
    message.pagination.page_size = 10
    message.pagination.total_pages = 1
    message.pagination.total_records = 1
    dumped = to_api_response_pagination_merchant_document(message).model_dump()
    assert dumped["data"][0]["id"] == 1
    assert dumped["pagination"]["total_records"] == 1


def test_document_trashed_pagination_delete_at() -> None:
    message = merchant_document_common_pb2.ApiResponsePaginationMerchantDocumentAt(
        status="success", message="ok"
    )
    message.data.add(document_id=9, merchant_id=2, document_type="NIB")
    message.data[0].deleted_at.value = "2026-02-03 00:00:00"
    dumped = to_api_response_pagination_merchant_document_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03 00:00:00"


def test_document_delete_and_all_envelopes_have_no_data() -> None:
    deleted = merchant_document_common_pb2.ApiResponseMerchantDocumentDelete(
        status="success", message="deleted"
    )
    all_message = merchant_document_common_pb2.ApiResponseMerchantDocumentAll(
        status="success", message="restored"
    )
    assert to_api_response_merchant_document_delete(deleted).model_dump() == {
        "status": "success",
        "message": "deleted",
        "data": None,
    }
    assert to_api_response_merchant_document_all(all_message).model_dump() == {
        "status": "success",
        "message": "restored",
        "data": None,
    }


def test_map_pagination_meta_none_defaults() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


__all__ = []
