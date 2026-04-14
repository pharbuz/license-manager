from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.license_manager.api.v1.schemas.common import BaseCamelSchema


class KindSchema(BaseCamelSchema):
    id: UUID
    name: str
    created_at: datetime
    modified_at: datetime


class KindCreateSchema(BaseCamelSchema):
    name: str


class KindUpdateSchema(BaseCamelSchema):
    name: str | None = Field(default=None)
