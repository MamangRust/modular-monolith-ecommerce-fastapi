"""Auth request DTOs. Validation Matches the expected `validator` tags. Two layers exist in and are kept here: - Gateway-facing DTOs (`AuthRequest`, `VerifyCodeRequest`, `ForgotPasswordRequest`, `ResetPasswordRequest`, `RefreshTokenRequest`) carry the `required`/`email`/`min=6` tags the gateway validates. `RegisterRequest` deliberately has no name/password-match constraints: the gateway validates `CreateUserRequest` (shared/domain/requests/user.py) before the RPC, exactly as auth handler does."""

from __future__ import annotations

from pydantic import BaseModel, Field

_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class AuthRequest(BaseModel):

    email: str = Field(..., pattern=_EMAIL)
    password: str = Field(..., min_length=6)


class VerifyCodeRequest(BaseModel):
    code: str = Field(..., min_length=1)


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., pattern=_EMAIL)


class ResetPasswordRequest(BaseModel):
    """does not enforce a password/confirm match in the validator; the service compares them and returns a 400 instead."""

    reset_token: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)


class CreateResetPasswordRequest(BaseModel):

    reset_token: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):

    firstname: str = ""
    lastname: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    verified_code: str = ""
    is_verified: bool = False


class CreateResetTokenRequest(BaseModel):
    user_id: int
    reset_token: str = Field(..., min_length=1)
    expired_at: str = Field(..., min_length=1)


class CreateRefreshToken(BaseModel):
    user_id: int = Field(..., ge=1)
    token: str = Field(..., min_length=1)
    expires_at: str = Field(..., min_length=1)


class UpdateRefreshToken(BaseModel):
    user_id: int = Field(..., ge=1)
    token: str = Field(..., min_length=1)
    expires_at: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class CreateUserRoleRequest(BaseModel):
    user_id: int
    role_id: int


class RemoveUserRoleRequest(BaseModel):
    user_id: int
    role_id: int


class JWTToken(BaseModel):
    token: str


__all__ = [
    "AuthRequest",
    "CreateRefreshToken",
    "CreateResetPasswordRequest",
    "CreateResetTokenRequest",
    "CreateUserRoleRequest",
    "ForgotPasswordRequest",
    "JWTToken",
    "RefreshTokenRequest",
    "RegisterRequest",
    "RemoveUserRoleRequest",
    "ResetPasswordRequest",
    "UpdateRefreshToken",
    "VerifyCodeRequest",
]
