"""review handler"""

from __future__ import annotations

from typing import Protocol


class ReviewQueryHandlerPort(Protocol):
    pass


class ReviewCommandHandlerPort(Protocol):
    pass


__all__ = [
    "ReviewCommandHandlerPort",
    "ReviewQueryHandlerPort",
]
