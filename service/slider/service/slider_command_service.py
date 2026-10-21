"""Slider command service. Every mutation invalidates the entire `slider:*` cache *after* the repository has committed — including `RestoreAll`/`DeleteAll`, which slider service DOES flush (unlike the shipping_address port, whose source forgets to). The repository error (e.g. a 404 `slider not found`) is propagated unchanged to the gRPC handler, which maps it through `ToGrpcError`, so a missing slider surfaces as `NOT_FOUND` on the wire."""

from __future__ import annotations

from pkg.database.schema.slider import CreateSliderRow, Slider, UpdateSliderRow
from pkg.logger.logger import Logger
from service.slider.redis.interfaces import SliderCommandCache
from service.slider.repository.interfaces import SliderCommandRepository
from shared.domain.requests.slider import CreateSliderRequest, UpdateSliderRequest
from shared.observability import Observability


class SliderCommandServiceImpl:
    def __init__(
        self,
        repo: SliderCommandRepository,
        cache: SliderCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(self, request: CreateSliderRequest) -> CreateSliderRow:
        with self._obs.span("slider.command.create"):
            slider = await self._repo.create(request)
            await self._cache.invalidate_slider_cache()
            self._logger.info("slider created", slider_id=slider.slider_id)
            return slider

    async def update(self, request: UpdateSliderRequest) -> UpdateSliderRow:
        slider_id = request.slider_id or 0
        with self._obs.span("slider.command.update", slider_id=slider_id):
            slider = await self._repo.update(request)
            await self._cache.invalidate_slider_cache()
            self._logger.info("slider updated", slider_id=slider_id)
            return slider

    async def trash(self, slider_id: int) -> Slider:
        with self._obs.span("slider.command.trash", slider_id=slider_id):
            slider = await self._repo.trash(slider_id)
            await self._cache.invalidate_slider_cache()
            self._logger.info("slider trashed", slider_id=slider_id)
            return slider

    async def restore(self, slider_id: int) -> Slider:
        with self._obs.span("slider.command.restore", slider_id=slider_id):
            slider = await self._repo.restore(slider_id)
            await self._cache.invalidate_slider_cache()
            self._logger.info("slider restored", slider_id=slider_id)
            return slider

    async def delete_permanent(self, slider_id: int) -> bool:
        with self._obs.span("slider.command.delete_permanent", slider_id=slider_id):
            await self._repo.delete_permanent(slider_id)
            await self._cache.invalidate_slider_cache()
            self._logger.info("slider deleted permanently", slider_id=slider_id)
            return True

    async def restore_all(self) -> bool:
        with self._obs.span("slider.command.restore_all"):
            await self._repo.restore_all()
            await self._cache.invalidate_slider_cache()
            self._logger.info("all sliders restored")
            return True

    async def delete_all_permanent(self) -> bool:
        with self._obs.span("slider.command.delete_all_permanent"):
            await self._repo.delete_all_permanent()
            await self._cache.invalidate_slider_cache()
            self._logger.info("all sliders deleted permanently")
            return True


__all__ = ["SliderCommandServiceImpl"]
