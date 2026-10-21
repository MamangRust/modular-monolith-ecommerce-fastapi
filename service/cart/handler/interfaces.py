"""cart handler"""

from __future__ import annotations

from typing import Protocol


class CartQueryHandlerPort(Protocol):
    pass


class CartCommandHandlerPort(Protocol):
    pass


__all__ = [
    "CartCommandHandlerPort",
    "CartQueryHandlerPort",
]
