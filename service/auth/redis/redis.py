"""Auth cache bundle."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logger.logger import Logger
from service.auth.redis.identity_cache import IdentityCacheImpl
from service.auth.redis.interfaces import (
    IdentityCache,
    LoginCache,
    PasswordResetCache,
    RegisterCache,
)
from service.auth.redis.login_cache import LoginCacheImpl
from service.auth.redis.password_cache import PasswordResetCacheImpl
from service.auth.redis.register_cache import RegisterCacheImpl
from shared.cache import CacheStore


@dataclass(frozen=True)
class Mencache:
    identity: IdentityCache
    login: LoginCache
    password_reset: PasswordResetCache
    register: RegisterCache


def new_mencache(store: CacheStore, logger: Logger) -> Mencache:
    return Mencache(
        identity=IdentityCacheImpl(store, logger),
        login=LoginCacheImpl(store, logger),
        password_reset=PasswordResetCacheImpl(store, logger),
        register=RegisterCacheImpl(store, logger),
    )


__all__ = ["Mencache", "new_mencache"]
