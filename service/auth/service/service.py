"""Auth service composition."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.auth import TokenManager
from pkg.hash import Hasher
from pkg.logger.logger import Logger
from service.auth.redis.redis import Mencache, new_mencache
from service.auth.repository.repository import Repositories
from service.auth.service.identity_service import IdentityServiceImpl
from service.auth.service.interfaces import (
    IdentifyService,
    LoginService,
    PasswordResetService,
    RegistrationService,
)
from service.auth.service.login_service import LoginServiceImpl
from service.auth.service.password_reset_service import PasswordResetServiceImpl
from service.auth.service.register_service import RegisterServiceImpl
from service.auth.service.token_service import TokenService
from shared.cache import CacheStore
from shared.observability import Observability

SERVICE_NAME = "auth-service"


@dataclass(frozen=True)
class Service:
    login: LoginService
    register: RegistrationService
    password_reset: PasswordResetService
    identify: IdentifyService


def new_service(
    repos: Repositories,
    cache_store: CacheStore,
    token: TokenManager,
    logger: Logger,
    hasher: Hasher | None = None,
) -> Service:
    obs = Observability(SERVICE_NAME, logger)
    cache: Mencache = new_mencache(cache_store, logger)
    hasher = hasher or Hasher()

    token_service = TokenService(token, repos.refresh_token, logger, obs)

    return Service(
        login=LoginServiceImpl(
            cache.login, repos.user, hasher, token_service, logger, obs
        ),
        register=RegisterServiceImpl(
            cache.register,
            repos.user,
            repos.role,
            repos.user_role,
            hasher,
            logger,
            obs,
        ),
        password_reset=PasswordResetServiceImpl(
            cache.password_reset,
            repos.user,
            repos.reset_token,
            hasher,
            logger,
            obs,
        ),
        identify=IdentityServiceImpl(
            cache.identity,
            token,
            repos.refresh_token,
            repos.user,
            token_service,
            logger,
            obs,
        ),
    )


__all__ = ["SERVICE_NAME", "Service", "new_service"]
