"""Slider service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.slider.redis.slider_command_cache import SliderCommandCacheImpl
from service.slider.redis.slider_query_cache import SliderQueryCacheImpl
from service.slider.repository.repository import Repositories
from service.slider.service.interfaces import (
    SliderCommandService,
    SliderQueryService,
)
from service.slider.service.slider_command_service import SliderCommandServiceImpl
from service.slider.service.slider_query_service import SliderQueryServiceImpl
from shared.cache import CacheStore
from shared.observability import Observability

SERVICE_NAME = "slider-service"


@dataclass(frozen=True)
class Service:
    slider_query: SliderQueryService
    slider_command: SliderCommandService


def new_service(
    repos: Repositories,
    cache_store: CacheStore,
    logger: Logger,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    return Service(
        slider_query=SliderQueryServiceImpl(
            repos.query, SliderQueryCacheImpl(cache_store, logger), logger, obs
        ),
        slider_command=SliderCommandServiceImpl(
            repos.command, SliderCommandCacheImpl(cache_store, logger), logger, obs
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]
