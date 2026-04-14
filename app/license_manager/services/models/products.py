from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.license_manager.services.models.common import BaseCamelModel


class ProductDto(BaseCamelModel):
    id: UUID
    name: str
    kind: str
    created_at: datetime
    modified_at: datetime


class ProductCreateDto(BaseCamelModel):
    name: str
    kind: str


class ProductUpdateDto(BaseCamelModel):
    name: str | None = Field(default=None)
    kind: str | None = Field(default=None)
