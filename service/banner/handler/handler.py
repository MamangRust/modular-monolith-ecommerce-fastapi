"""Banner handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.banner.handler.command import BannerCommandHandler
from service.banner.handler.query import BannerQueryHandler
from service.banner.service.service import Service


@dataclass(frozen=True)
class Handler:
    banner_query: BannerQueryHandler
    banner_command: BannerCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        banner_query=BannerQueryHandler(service.banner_query, logger),
        banner_command=BannerCommandHandler(service.banner_command, logger),
    )


__all__ = ["Handler", "new_handler"]
