"""Slider handler package."""

from service.slider.handler.command import SliderCommandHandler
from service.slider.handler.handler import Handler, new_handler
from service.slider.handler.query import SliderQueryHandler

__all__ = ["SliderCommandHandler", "SliderQueryHandler", "Handler", "new_handler"]
