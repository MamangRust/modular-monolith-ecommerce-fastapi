"""Role request DTOs."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class FindAllRoles(BaseModel):
    search: str = ""
    page: int = 1
    page_size: int = 10

    @model_validator(mode="after")
    def _clamp_pagination(self) -> FindAllRoles:
        if self.page <= 0:
            self.page = 1
        if self.page_size <= 0:
            self.page_size = 10
        if self.page_size > 100:
            self.page_size = 100
        return self


class CreateRoleRequest(BaseModel):
    name: str = Field(..., min_length=1)


class UpdateRoleRequest(BaseModel):
    id: int | None = None
    name: str = Field(..., min_length=1)


class RoleRequestPayload(BaseModel):
    user_id: int = 0
    correlation_id: str = ""
    reply_topic: str = ""
