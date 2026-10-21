"""Slider handler composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.slider.handler.command import SliderCommandHandler
from service.slider.handler.query import SliderQueryHandler
from service.slider.service.service import Service


@dataclass(frozen=True)
class Handler:
    slider_query: SliderQueryHandler
    slider_command: SliderCommandHandler


def new_handler(service: Service, logger: Logger) -> Handler:
    return Handler(
        slider_query=SliderQueryHandler(service.slider_query, logger),
        slider_command=SliderCommandHandler(service.slider_command, logger),
    )


__all__ = ["Handler", "new_handler"]
