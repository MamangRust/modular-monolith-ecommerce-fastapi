"""Banner command service. Every mutation invalidates the banner cache *after* the repository has committed — by-id plus the list patterns. This is the deviation called out in the plan: the banner service only dropped `banner:id:*` on Update/Trash/Restore/DeletePermanent and never touched list caches, so list reads stayed stale for up to the 5-minute TTL."""

from __future__ import annotations

from pkg.database.schema.banner import (
    Banner,
    CreateBannerRow,
    UpdateBannerRow,
)
from pkg.logger.logger import Logger
from service.banner.redis.interfaces import BannerCommandCache
from service.banner.repository.interfaces import BannerCommandRepository
from shared.domain.requests.banner import CreateBannerRequest, UpdateBannerRequest
from shared.observability import Observability


class BannerCommandServiceImpl:
    def __init__(
        self,
        repo: BannerCommandRepository,
        cache: BannerCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(self, request: CreateBannerRequest) -> CreateBannerRow:
        with self._obs.span("banner.command.create"):
            banner = await self._repo.create(request)
            await self._cache.invalidate_lists()
            self._logger.info("banner created", banner_id=banner.banner_id)
            return banner

    async def update(self, request: UpdateBannerRequest) -> UpdateBannerRow:
        banner_id = request.banner_id or 0
        with self._obs.span("banner.command.update", banner_id=banner_id):
            banner = await self._repo.update(request)
            await self._cache.invalidate_banner(banner_id)
            self._logger.info("banner updated", banner_id=banner_id)
            return banner

    async def trash(self, banner_id: int) -> Banner:
        with self._obs.span("banner.command.trash", banner_id=banner_id):
            banner = await self._repo.trash(banner_id)
            await self._cache.invalidate_banner(banner_id)
            self._logger.info("banner trashed", banner_id=banner_id)
            return banner

    async def restore(self, banner_id: int) -> Banner:
        with self._obs.span("banner.command.restore", banner_id=banner_id):
            banner = await self._repo.restore(banner_id)
            await self._cache.invalidate_banner(banner_id)
            self._logger.info("banner restored", banner_id=banner_id)
            return banner

    async def delete_permanent(self, banner_id: int) -> None:
        with self._obs.span("banner.command.delete_permanent", banner_id=banner_id):
            await self._repo.delete_permanent(banner_id)
            await self._cache.invalidate_banner(banner_id)
            self._logger.info("banner deleted permanently", banner_id=banner_id)

    async def restore_all(self) -> None:
        with self._obs.span("banner.command.restore_all"):
            await self._repo.restore_all()
            await self._cache.invalidate_all()
            self._logger.info("all banners restored")

    async def delete_all_permanent(self) -> None:
        with self._obs.span("banner.command.delete_all_permanent"):
            await self._repo.delete_all_permanent()
            await self._cache.invalidate_all()
            self._logger.info("all banners deleted permanently")


__all__ = ["BannerCommandServiceImpl"]
