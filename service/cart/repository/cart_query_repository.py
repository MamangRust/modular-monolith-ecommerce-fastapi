"""cart read repository. SQL is kept verbatim from the reference where practical, including the `COUNT(*) OVER` window that supplies `total_count` in the same round trip as the page."""

from __future__ import annotations

from pkg.database.database import Database
from pkg.database.schema.cart import GetCartsRow
from shared.domain.requests.cart import FindAllCarts
from shared.errors import err_find_all_carts

_GET_CARTS = """
SELECT
    cart_id,
    user_id,
    product_id,
    name,
    price,
    image,
    quantity,
    weight,
    created_at,
    updated_at,
    COUNT(*) OVER () AS total_count
FROM carts
WHERE
    deleted_at IS NULL
    AND user_id = :user_id
    AND (
        name ILIKE '%' || :search || '%'
        OR price::TEXT ILIKE '%' || :search || '%'
    )
ORDER BY created_at DESC
LIMIT :limit
OFFSET
    :offset
"""


class CartQueryRepositoryImpl:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_all(self, request: FindAllCarts) -> list[GetCartsRow]:
        offset = (request.page - 1) * request.page_size
        params = {
            "user_id": request.user_id,
            "search": request.search,
            "limit": request.page_size,
            "offset": offset,
        }
        try:
            rows = await self._db.select(_GET_CARTS, params)
        except Exception as exc:
            raise err_find_all_carts.with_internal(exc) from exc
        return [GetCartsRow.from_row(row) for row in rows]


__all__ = ["CartQueryRepositoryImpl"]
