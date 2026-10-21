"""Banner row/proto -> response DTO mapping. Two input shapes, one output: - row dataclasses — format the date/time/timestamp values the way the handlers do; - proto messages — already-formatted strings, passed through unchanged. Timestamps use the banner-specific `%Y-%m-%d %H:%M:%S.mmm` layout, dates `%Y-%m-%d` and clock times `%H:%M:%S`. Do not unify with the role/user layouts: the banner handler deliberately differs."""

from __future__ import annotations

from typing import Any

from pkg.database.schema.banner import (
    Banner,
    CreateBannerRow,
    GetBannerRow,
    GetBannersActiveRow,
    GetBannersRow,
    UpdateBannerRow,
)
from shared.convert.convert import (
    format_clock,
    format_iso_date,
    format_timestamp_millis,
)
from shared.domain.response.banner import BannerResponse, BannerResponseDeleteAt

BannerRow = (
    Banner | CreateBannerRow | GetBannerRow | GetBannersRow | UpdateBannerRow
)
BannerDeleteAtRow = Banner | GetBannersActiveRow


def to_banner_response(row: BannerRow) -> BannerResponse:
    return BannerResponse(
        id=row.banner_id,
        name=row.name,
        start_date=format_iso_date(row.start_date),
        end_date=format_iso_date(row.end_date),
        start_time=format_clock(row.start_time),
        end_time=format_clock(row.end_time),
        is_active=row.is_active,
        created_at=format_timestamp_millis(row.created_at),
        updated_at=format_timestamp_millis(row.updated_at),
    )


def to_banner_response_delete_at(row: BannerDeleteAtRow) -> BannerResponseDeleteAt:
    return BannerResponseDeleteAt(
        id=row.banner_id,
        name=row.name,
        start_date=format_iso_date(row.start_date),
        end_date=format_iso_date(row.end_date),
        start_time=format_clock(row.start_time),
        end_time=format_clock(row.end_time),
        is_active=row.is_active,
        created_at=format_timestamp_millis(row.created_at),
        updated_at=format_timestamp_millis(row.updated_at),
        deleted_at=format_timestamp_millis(row.deleted_at) or None,
    )


def map_banner_response(pb: Any) -> BannerResponse:
    return BannerResponse(
        id=int(pb.banner_id),
        name=pb.name,
        start_date=pb.start_date,
        end_date=pb.end_date,
        start_time=pb.start_time,
        end_time=pb.end_time,
        is_active=pb.is_active,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_banner_response_delete_at(pb: Any) -> BannerResponseDeleteAt:
    # always sets the pointer, so an absent wrapper renders as "".
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return BannerResponseDeleteAt(
        id=int(pb.banner_id),
        name=pb.name,
        start_date=pb.start_date,
        end_date=pb.end_date,
        start_time=pb.start_time,
        end_time=pb.end_time,
        is_active=pb.is_active,
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
    )


__all__ = [
    "map_banner_response",
    "map_banner_response_delete_at",
    "to_banner_response",
    "to_banner_response_delete_at",
]
