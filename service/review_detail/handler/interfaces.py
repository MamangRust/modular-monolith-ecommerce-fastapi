"""Review detail handler"""

from __future__ import annotations

from typing import Protocol


class ReviewDetailQueryHandlerPort(Protocol):
    pass


class ReviewDetailCommandHandlerPort(Protocol):
    pass


__all__ = ["ReviewDetailCommandHandlerPort", "ReviewDetailQueryHandlerPort"]
