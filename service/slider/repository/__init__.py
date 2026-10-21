"""Slider repository package."""

from service.slider.repository.interfaces import (
    SliderCommandRepository,
    SliderQueryRepository,
)
from service.slider.repository.repository import Repositories, new_repositories

__all__ = [
    "SliderCommandRepository",
    "SliderQueryRepository",
    "Repositories",
    "new_repositories",
]
