"""Row types for the merchant_documents table. The proto/REST `uploaded_at` is *not* taken from the DB `uploaded_at` column: handler mapping fills `UploadedAt` from `CreatedAt`, so the `uploaded_at` column is selected but effectively ignored by the wire response. `uploaded_at` is still part of every row (the create statement writes it), so it is modelled here. `note` is nullable in (`*string`). Timestamps surface as `datetime.datetime` and are formatted `%Y-%m-%d %H:%M:%S`."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class MerchantDocument:

    document_id: int
    merchant_id: int
    document_type: str
    document_url: str
    status: str
    note: str | None
    uploaded_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> MerchantDocument:
        return cls(
            document_id=row["document_id"],
            merchant_id=row["merchant_id"],
            document_type=row["document_type"],
            document_url=row["document_url"],
            status=row["status"],
            note=row.get("note"),
            uploaded_at=row["uploaded_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )


@dataclass
class CreateMerchantDocumentRow:
    """`Create`/`Update`/`UpdateStatus`/`FindById` projection (no `deleted_at`)."""

    document_id: int
    merchant_id: int
    document_type: str
    document_url: str
    status: str
    note: str | None
    uploaded_at: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> CreateMerchantDocumentRow:
        return cls(
            document_id=row["document_id"],
            merchant_id=row["merchant_id"],
            document_type=row["document_type"],
            document_url=row["document_url"],
            status=row["status"],
            note=row.get("note"),
            uploaded_at=row["uploaded_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


GetMerchantDocumentRow = CreateMerchantDocumentRow
UpdateMerchantDocumentRow = CreateMerchantDocumentRow
UpdateMerchantDocumentStatusRow = CreateMerchantDocumentRow


@dataclass
class GetMerchantDocumentsRow:
    """`FindAll` projection with a window total count."""

    document_id: int
    merchant_id: int
    document_type: str
    document_url: str
    status: str
    note: str | None
    uploaded_at: datetime
    created_at: datetime
    updated_at: datetime
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetMerchantDocumentsRow:
        return cls(
            document_id=row["document_id"],
            merchant_id=row["merchant_id"],
            document_type=row["document_type"],
            document_url=row["document_url"],
            status=row["status"],
            note=row.get("note"),
            uploaded_at=row["uploaded_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_count=int(row["total_count"]),
        )


@dataclass
class GetActiveMerchantDocumentsRow:
    """`FindActive`/`FindTrashed` projection: carries `deleted_at` + total."""

    document_id: int
    merchant_id: int
    document_type: str
    document_url: str
    status: str
    note: str | None
    uploaded_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    total_count: int

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> GetActiveMerchantDocumentsRow:
        return cls(
            document_id=row["document_id"],
            merchant_id=row["merchant_id"],
            document_type=row["document_type"],
            document_url=row["document_url"],
            status=row["status"],
            note=row.get("note"),
            uploaded_at=row["uploaded_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
            total_count=int(row["total_count"]),
        )


GetTrashedMerchantDocumentsRow = GetActiveMerchantDocumentsRow


__all__ = [
    "CreateMerchantDocumentRow",
    "GetActiveMerchantDocumentsRow",
    "GetMerchantDocumentRow",
    "GetMerchantDocumentsRow",
    "GetTrashedMerchantDocumentsRow",
    "MerchantDocument",
    "UpdateMerchantDocumentRow",
    "UpdateMerchantDocumentStatusRow",
]
