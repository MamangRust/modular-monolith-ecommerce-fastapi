"""Gateway middlewares: JWT auth, role validation, RBAC.

`RoleValidator` is the legacy payment-gateway Kafka request/reply validator,
kept for reference only — the ecommerce gateway wires `RoleValidatorGRPC`."""

from service.apigateway.middlewares.auth import (
    PUBLIC_PATHS,
    PUBLIC_PREFIXES,
    JwtAuthMiddleware,
    is_public_path,
)
from service.apigateway.middlewares.required_role import RoleDependency, require_roles
from service.apigateway.middlewares.role_grpc import RoleValidatorGRPC
from service.apigateway.middlewares.role_validator import RoleValidator

__all__ = [
    "PUBLIC_PATHS",
    "PUBLIC_PREFIXES",
    "JwtAuthMiddleware",
    "RoleDependency",
    "RoleValidator",
    "RoleValidatorGRPC",
    "is_public_path",
    "require_roles",
]
