"""cart query service. Reads are cache-first: a miss loads from the DB and populates the cache with the page and its window `total_count` (taken from the first row; 0 when the page is empty). `FindAll` returns the repository error unchanged on failure, so a read failure keeps `err_find_all_carts` (500). NORMALISATION: clamps `page <= 0 → 1` / `pageSize <= 0 → 10` inside the service (`cartQueryService.FindAll`). Like the other domains, that clamp lives in the gRPC handler (`normalize_page`), so the service receives already-normalised paging."""

from __future__ import annotations

from pkg.database.schema.cart import GetCartsRow
from pkg.logger.logger import Logger
from service.cart.redis.interfaces import CartQueryCache
from service.cart.repository.interfaces import CartQueryRepository
from shared.domain.requests.cart import FindAllCarts
from shared.observability import Observability


class CartQueryServiceImpl:
    def __init__(
        self,
        repo: CartQueryRepository,
        cache: CartQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(self, request: FindAllCarts) -> tuple[list[GetCartsRow], int]:
        with self._obs.span(
            "cart.query.find_all",
            page=request.page,
            page_size=request.page_size,
            search=request.search,
        ):
            cached = await self._cache.get_carts(request)
            if cached is not None:
                return cached
            rows = await self._repo.find_all(request)
            total = rows[0].total_count if rows else 0
            await self._cache.set_carts(request, rows, total)
            return rows, total


__all__ = ["CartQueryServiceImpl"]
