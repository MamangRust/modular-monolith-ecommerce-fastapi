"""Merchant row/proto -> response DTO mapping. Two input shapes, one output: - row dataclasses — format the timestamp values as `%Y-%m-%d %H:%M:%S` to match the `2006-01-02 15:04:05` layout (a new format for this domain; see the). A NULL `description`/`address`/`contact_email`/`contact_phone`/`note` becomes `""` because `getString` collapses the nil pointer; - proto messages — already-formatted timestamp strings, passed through unchanged. The document REST `created_at` is filled from the row `created_at` (handler mapping sets proto `uploaded_at` from `created_at`, and the REST mapper copies it back into `created_at`), so the DB `uploaded_at` column never reaches the wire."""

from __future__ import annotations

from typing import Any

from pkg.database.schema.merchant import (
    CreateMerchantRow,
    GetMerchantByIDRow,
    GetMerchantsActiveRow,
    GetMerchantsRow,
    Merchant,
    UpdateMerchantRow,
    UpdateMerchantStatusRow,
)
from pkg.database.schema.merchant_document import (
    CreateMerchantDocumentRow,
    GetActiveMerchantDocumentsRow,
    GetMerchantDocumentRow,
    GetMerchantDocumentsRow,
    MerchantDocument,
    UpdateMerchantDocumentRow,
    UpdateMerchantDocumentStatusRow,
)
from shared.convert.convert import format_time_ptr
from shared.domain.response.merchant import (
    MerchantDocumentResponse,
    MerchantDocumentResponseDeleteAt,
    MerchantResponse,
    MerchantResponseDeleteAt,
)
from shared.domain.response.responses import PaginationMeta

MerchantRow = (
    Merchant
    | CreateMerchantRow
    | GetMerchantByIDRow
    | GetMerchantsRow
    | UpdateMerchantRow
    | UpdateMerchantStatusRow
)
MerchantDeleteAtRow = Merchant | GetMerchantsActiveRow

MerchantDocumentRow = (
    MerchantDocument
    | CreateMerchantDocumentRow
    | GetMerchantDocumentRow
    | GetMerchantDocumentsRow
    | UpdateMerchantDocumentRow
    | UpdateMerchantDocumentStatusRow
)
MerchantDocumentDeleteAtRow = MerchantDocument | GetActiveMerchantDocumentsRow


def to_merchant_response(row: MerchantRow) -> MerchantResponse:
    return MerchantResponse(
        id=row.merchant_id,
        user_id=row.user_id,
        name=row.name,
        description=row.description or "",
        address=row.address or "",
        contact_email=row.contact_email or "",
        contact_phone=row.contact_phone or "",
        status=row.status,
        created_at=format_time_ptr(row.created_at),
        updated_at=format_time_ptr(row.updated_at),
    )


def to_merchant_response_delete_at(row: MerchantDeleteAtRow) -> MerchantResponseDeleteAt:
    return MerchantResponseDeleteAt(
        id=row.merchant_id,
        user_id=row.user_id,
        name=row.name,
        description=row.description or "",
        address=row.address or "",
        contact_email=row.contact_email or "",
        contact_phone=row.contact_phone or "",
        status=row.status,
        created_at=format_time_ptr(row.created_at),
        updated_at=format_time_ptr(row.updated_at),
        # always attaches the pointer, so a live row renders as "".
        deleted_at=format_time_ptr(row.deleted_at),
    )


def map_merchant_response(pb: Any) -> MerchantResponse:
    return MerchantResponse(
        id=int(pb.id),
        user_id=int(pb.user_id),
        name=pb.name,
        description=pb.description,
        address=pb.address,
        contact_email=pb.contact_email,
        contact_phone=pb.contact_phone,
        status=pb.status,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_merchant_response_delete_at(pb: Any) -> MerchantResponseDeleteAt:
    # always sets the pointer, so an absent wrapper renders as "".
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return MerchantResponseDeleteAt(
        id=int(pb.id),
        user_id=int(pb.user_id),
        name=pb.name,
        description=pb.description,
        address=pb.address,
        contact_email=pb.contact_email,
        contact_phone=pb.contact_phone,
        status=pb.status,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
    )


def to_merchant_document_response(row: MerchantDocumentRow) -> MerchantDocumentResponse:
    return MerchantDocumentResponse(
        id=row.document_id,
        merchant_id=row.merchant_id,
        document_type=row.document_type,
        document_url=row.document_url,
        status=row.status,
        note=row.note or "",
        created_at=format_time_ptr(row.created_at),
        updated_at=format_time_ptr(row.updated_at),
    )


def to_merchant_document_response_delete_at(
    row: MerchantDocumentDeleteAtRow,
) -> MerchantDocumentResponseDeleteAt:
    return MerchantDocumentResponseDeleteAt(
        id=row.document_id,
        merchant_id=row.merchant_id,
        document_type=row.document_type,
        document_url=row.document_url,
        status=row.status,
        note=row.note or "",
        created_at=format_time_ptr(row.created_at),
        updated_at=format_time_ptr(row.updated_at),
        deleted_at=format_time_ptr(row.deleted_at),
    )


def map_merchant_document_response(pb: Any) -> MerchantDocumentResponse:
    # proto `document_id` -> REST `id`; REST `created_at` <- proto `uploaded_at`.
    return MerchantDocumentResponse(
        id=int(pb.document_id),
        merchant_id=int(pb.merchant_id),
        document_type=pb.document_type,
        document_url=pb.document_url,
        status=pb.status,
        note=pb.note,
        created_at=pb.uploaded_at,
        updated_at=pb.updated_at,
    )


def map_merchant_document_response_delete_at(
    pb: Any,
) -> MerchantDocumentResponseDeleteAt:
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return MerchantDocumentResponseDeleteAt(
        id=int(pb.document_id),
        merchant_id=int(pb.merchant_id),
        document_type=pb.document_type,
        document_url=pb.document_url,
        status=pb.status,
        note=pb.note,
        created_at=pb.uploaded_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
    )


def map_pagination_meta(meta: Any) -> PaginationMeta:
    if meta is None:
        return PaginationMeta()
    return PaginationMeta(
        current_page=int(meta.current_page),
        page_size=int(meta.page_size),
        total_pages=int(meta.total_pages),
        total_records=int(meta.total_records),
    )


__all__ = [
    "map_merchant_document_response",
    "map_merchant_document_response_delete_at",
    "map_merchant_response",
    "map_merchant_response_delete_at",
    "map_pagination_meta",
    "to_merchant_document_response",
    "to_merchant_document_response_delete_at",
    "to_merchant_response",
    "to_merchant_response_delete_at",
]
