"""User request DTOs. Validation Matches the expected `validator` tags: `alpha` names, a plain email shape, a 6-char minimum password, and `eqfield=Password` confirmation. The `email` check is a regex rather than pydantic's EmailStr so not pull in `email-validator`."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

_ALPHA = r"^[A-Za-z]+$"
_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class FindAllUsers(BaseModel):
    search: str = ""
    page: int = 1
    page_size: int = 10

    @model_validator(mode="after")
    def _clamp_pagination(self) -> FindAllUsers:
        if self.page < 1:
            self.page = 1
        if self.page_size < 1:
            self.page_size = 10
        if self.page_size > 100:
            self.page_size = 100
        return self


class CreateUserRequest(BaseModel):
    firstname: str = Field(..., min_length=1, pattern=_ALPHA)
    lastname: str = Field(..., min_length=1, pattern=_ALPHA)
    email: str = Field(..., pattern=_EMAIL)
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def _passwords_match(self) -> CreateUserRequest:
        if self.password != self.confirm_password:
            raise ValueError("confirm_password must match password")
        return self


class UpdateUserRequest(BaseModel):
    user_id: int | None = None
    firstname: str = Field(..., min_length=1, pattern=_ALPHA)
    lastname: str = Field(..., min_length=1, pattern=_ALPHA)
    email: str = Field(..., pattern=_EMAIL)
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def _passwords_match(self) -> UpdateUserRequest:
        if self.password != self.confirm_password:
            raise ValueError("confirm_password must match password")
        return self


__all__ = ["CreateUserRequest", "FindAllUsers", "UpdateUserRequest"]
