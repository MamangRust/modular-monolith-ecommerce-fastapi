"""Slider repository composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.database.database import Database
from service.slider.repository.interfaces import (
    SliderCommandRepository,
    SliderQueryRepository,
)
from service.slider.repository.slider_command_repository import (
    SliderCommandRepositoryImpl,
)
from service.slider.repository.slider_query_repository import (
    SliderQueryRepositoryImpl,
)


@dataclass(frozen=True)
class Repositories:
    query: SliderQueryRepository
    command: SliderCommandRepository


def new_repositories(db: Database) -> Repositories:
    return Repositories(
        query=SliderQueryRepositoryImpl(db),
        command=SliderCommandRepositoryImpl(db),
    )


__all__ = ["Repositories", "new_repositories"]
