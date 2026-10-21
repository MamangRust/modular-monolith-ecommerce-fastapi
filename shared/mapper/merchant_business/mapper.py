"""merchant_business proto -> response DTO mapping. Two proto shapes, one output family: - `MerchantBusinessResponse` (Create/Update/FindById, FindAll list); - `MerchantBusinessResponseDeleteAt` (active/trashed lists, trash/restore). The proto already carries formatted strings (`%Y-%m-%d %H:%M:%S.mmm`), so this layer only shapes them into the REST envelopes. the mapper copies `merchant_name` from the proto, but the handler never fills it, so it is always `""`. `deleted_at` renders as `""` when no wrapper is attached (takes the address of a zero string)."""

from __future__ import annotations

from typing import Any

from shared.domain.response.merchant_business import (
    MerchantBusinessResponse,
    MerchantBusinessResponseDeleteAt,
)
from shared.domain.response.responses import PaginationMeta


def map_merchant_business_response(pb: Any) -> MerchantBusinessResponse:
    return MerchantBusinessResponse(
        id=int(pb.id),
        merchant_id=int(pb.merchant_id),
        business_type=pb.business_type,
        tax_id=pb.tax_id,
        established_year=int(pb.established_year),
        number_of_employees=int(pb.number_of_employees),
        website_url=pb.website_url,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        merchant_name=pb.merchant_name,
    )


def map_merchant_business_response_delete_at(
    pb: Any,
) -> MerchantBusinessResponseDeleteAt:
    # takes the address of a zero string when no wrapper is attached, so a
    # live row renders `deleted_at: ""`.
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return MerchantBusinessResponseDeleteAt(
        id=int(pb.id),
        merchant_id=int(pb.merchant_id),
        business_type=pb.business_type,
        tax_id=pb.tax_id,
        established_year=int(pb.established_year),
        number_of_employees=int(pb.number_of_employees),
        website_url=pb.website_url,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        merchant_name=pb.merchant_name,
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
    "map_merchant_business_response",
    "map_merchant_business_response_delete_at",
    "map_pagination_meta",
]
