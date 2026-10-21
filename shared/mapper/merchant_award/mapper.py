"""merchant_award proto -> response DTO mapping. Two proto shapes, one output family: - `MerchantAwardResponse` (Create/Update/FindById, FindAll list); - `MerchantAwardResponseDeleteAt` (active/trashed lists, trash/restore). The proto already carries formatted strings (dates `%Y-%m-%d`, timestamps `%Y-%m-%d %H:%M:%S.mmm`), so this layer only shapes them into the REST envelopes. `merchant_name` is never copied (the mapper leaves it at the zero value). `deleted_at` renders as `""` when no wrapper is attached (takes the address of a zero string)."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant_award import (
    MerchantAwardResponse,
    MerchantAwardResponseDeleteAt,
)
from shared.domain.response.responses import PaginationMeta


def map_merchant_award_response(pb: Any) -> MerchantAwardResponse:
    return MerchantAwardResponse(
        id=int(pb.id),
        merchant_id=int(pb.merchant_id),
        title=pb.title,
        description=pb.description,
        issued_by=pb.issued_by,
        issue_date=pb.issue_date,
        expiry_date=pb.expiry_date,
        certificate_url=pb.certificate_url,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_merchant_award_response_delete_at(
    pb: Any,
) -> MerchantAwardResponseDeleteAt:
    # takes the address of a zero string when no wrapper is attached, so a
    # live row renders `deleted_at: ""`.
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return MerchantAwardResponseDeleteAt(
        id=int(pb.id),
        merchant_id=int(pb.merchant_id),
        title=pb.title,
        description=pb.description,
        issued_by=pb.issued_by,
        issue_date=pb.issue_date,
        expiry_date=pb.expiry_date,
        certificate_url=pb.certificate_url,
        created_at=pb.created_at,
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
    "map_merchant_award_response",
    "map_merchant_award_response_delete_at",
    "map_pagination_meta",
]
