"""Slider service package."""

from service.slider.service.interfaces import (
    SliderCommandService,
    SliderQueryService,
)
from service.slider.service.service import SERVICE_NAME, Service, new_service

__all__ = [
    "SERVICE_NAME",
    "SliderCommandService",
    "SliderQueryService",
    "Service",
    "new_service",
]
