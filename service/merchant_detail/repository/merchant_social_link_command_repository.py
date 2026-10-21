"""merchant_social_link write repository. `create`/`update` return the `RETURNING` row (None -> not found). `trash`/ `restore` are `:one` in (they carry `RETURNING`), so a missing row yields `pgx.ErrNoRows` -> `err_merchant_social_link_not_found`; `delete_permanent`/ `restore_all`/`delete_all` are `:exec`, so they ignore affected rows and always report success."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from pkg.database.database import Database
from pkg.database.schema.merchant_detail import (
    CreateMerchantSocialMediaLinkRow,
    UpdateMerchantSocialMediaLinkRow,
)
from shared.domain.requests.merchant_detail import (
    CreateMerchantSocialRequest,
    UpdateMerchantSocialRequest,
)
from shared.errors import (
    AppError,
    err_create_merchant_social_link,
    err_delete_all_permanent_merchant_social_links,
    err_delete_permanent_merchant_social_link,
    err_merchant_social_link_not_found,
    err_restore_all_merchant_social_links,
    err_restore_merchant_social_link,
    err_trash_merchant_social_link,
    err_update_merchant_social_link,
)

_RETURNING_COLUMNS = """
    merchant_social_id,
    merchant_detail_id,
    platform,
    url,
    created_at,
    updated_at
"""

_CREATE_MERCHANT_SOCIAL_LINK = f"""
INSERT INTO merchant_social_media_links (
    merchant_detail_id, platform, url
)
VALUES (
    :merchant_detail_id, :platform, :url
)
RETURNING
{_RETURNING_COLUMNS}
"""

_UPDATE_MERCHANT_SOCIAL_LINK = f"""
UPDATE merchant_social_media_links
SET
    platform = :platform,
    url = :url,
    updated_at = CURRENT_TIMESTAMP
WHERE
    merchant_social_id = :merchant_social_id
RETURNING
{_RETURNING_COLUMNS}
"""

_TRASH_MERCHANT_SOCIAL_LINK = f"""
UPDATE merchant_social_media_links
SET deleted_at = CURRENT_TIMESTAMP
WHERE
    merchant_social_id = :merchant_social_id
    AND deleted_at IS NULL
RETURNING
{_RETURNING_COLUMNS},
    deleted_at
"""

_RESTORE_MERCHANT_SOCIAL_LINK = f"""
UPDATE merchant_social_media_links
SET deleted_at = NULL
WHERE
    merchant_social_id = :merchant_social_id
    AND deleted_at IS NOT NULL
RETURNING
{_RETURNING_COLUMNS},
    deleted_at
"""

_DELETE_MERCHANT_SOCIAL_LINK_PERMANENTLY = """
DELETE FROM merchant_social_media_links
WHERE merchant_social_id = :merchant_social_id
"""

_RESTORE_ALL_MERCHANT_SOCIAL_LINKS = (
    "UPDATE merchant_social_media_links SET deleted_at = NULL "
    "WHERE deleted_at IS NOT NULL"
)

_DELETE_ALL_MERCHANT_SOCIAL_LINKS_PERMANENTLY = (
    "DELETE FROM merchant_social_media_links WHERE deleted_at IS NOT NULL"
)


class MerchantSocialLinkCommandRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def _returning(
        self,
        sql: str,
        params: dict[str, Any],
        conn: AsyncConnection | None = None,
    ) -> dict[str, Any] | None:
        if conn is None:
            return await self._db.execute(sql, params)
        result = await conn.execute(text(sql), params)
        if not result.returns_rows:
            return None
        row = result.mappings().first()
        return dict(row) if row is not None else None

    async def create(
        self, request: CreateMerchantSocialRequest
    ) -> CreateMerchantSocialMediaLinkRow:
        params = {
            "merchant_detail_id": request.merchant_detail_id,
            "platform": request.platform,
            "url": request.url,
        }
        try:
            row = await self._returning(_CREATE_MERCHANT_SOCIAL_LINK, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_create_merchant_social_link.with_internal(exc) from exc
        if row is None:
            raise err_merchant_social_link_not_found
        return CreateMerchantSocialMediaLinkRow.from_row(row)

    async def update(
        self, request: UpdateMerchantSocialRequest
    ) -> UpdateMerchantSocialMediaLinkRow:
        params = {
            "merchant_social_id": request.id,
            "platform": request.platform,
            "url": request.url,
        }
        try:
            row = await self._returning(_UPDATE_MERCHANT_SOCIAL_LINK, params)
        except AppError:
            raise
        except Exception as exc:
            raise err_update_merchant_social_link.with_internal(exc) from exc
        if row is None:
            raise err_merchant_social_link_not_found
        return UpdateMerchantSocialMediaLinkRow.from_row(row)

    async def trash(self, social_id: int) -> bool:
        try:
            row = await self._returning(
                _TRASH_MERCHANT_SOCIAL_LINK, {"merchant_social_id": social_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_trash_merchant_social_link.with_internal(exc) from exc
        if row is None:
            raise err_merchant_social_link_not_found
        return True

    async def restore(self, social_id: int) -> bool:
        try:
            row = await self._returning(
                _RESTORE_MERCHANT_SOCIAL_LINK, {"merchant_social_id": social_id}
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_merchant_social_link.with_internal(exc) from exc
        if row is None:
            raise err_merchant_social_link_not_found
        return True

    async def delete_permanent(self, social_id: int) -> bool:
        try:
            await self._db.execute(
                _DELETE_MERCHANT_SOCIAL_LINK_PERMANENTLY,
                {"merchant_social_id": social_id},
            )
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_permanent_merchant_social_link.with_internal(
                exc
            ) from exc
        return True

    async def restore_all(self) -> bool:
        try:
            await self._db.execute(_RESTORE_ALL_MERCHANT_SOCIAL_LINKS)
        except AppError:
            raise
        except Exception as exc:
            raise err_restore_all_merchant_social_links.with_internal(exc) from exc
        return True

    async def delete_all(self) -> bool:
        try:
            await self._db.execute(_DELETE_ALL_MERCHANT_SOCIAL_LINKS_PERMANENTLY)
        except AppError:
            raise
        except Exception as exc:
            raise err_delete_all_permanent_merchant_social_links.with_internal(
                exc
            ) from exc
        return True


__all__ = ["MerchantSocialLinkCommandRepositoryImpl"]
