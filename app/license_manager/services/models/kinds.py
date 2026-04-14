from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.license_manager.services.models.common import BaseCamelModel


class KindDto(BaseCamelModel):
    id: UUID
    name: str
    created_at: datetime
    modified_at: datetime


class KindCreateDto(BaseCamelModel):
    name: str


class KindUpdateDto(BaseCamelModel):
    name: str | None = Field(default=None)
