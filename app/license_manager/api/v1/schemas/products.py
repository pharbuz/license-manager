from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.license_manager.api.v1.schemas.common import BaseCamelSchema


class ProductSchema(BaseCamelSchema):
    id: UUID
    name: str
    kind: str
    created_at: datetime
    modified_at: datetime


class ProductCreateSchema(BaseCamelSchema):
    name: str
    kind: str


class ProductUpdateSchema(BaseCamelSchema):
    name: str | None = Field(default=None)
    kind: str | None = Field(default=None)
