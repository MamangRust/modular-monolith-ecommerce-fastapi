"""product handler"""

from __future__ import annotations

from typing import Protocol


class ProductQueryHandlerPort(Protocol):
    pass


class ProductCommandHandlerPort(Protocol):
    pass


__all__ = [
    "ProductCommandHandlerPort",
    "ProductQueryHandlerPort",
]
