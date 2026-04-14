from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import ConfigDict, Field

from app.license_manager.api.v1.schemas.common import BaseCamelSchema


class AuditLogQueryParams(BaseCamelSchema):
    entity_type: str | None = None
    entity_id: str | None = None
    request_id: str | None = None
    actor_id: str | None = None
    source: str | None = None
    occurred_from: datetime | None = None
    occurred_to: datetime | None = None


class AuditLogEntrySchema(BaseCamelSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actor_id: str | None = None
    actor_type: str
    actor_display_name: str | None = None
    source: str
    request_id: str | None = None
    action: str
    entity_type: str
    entity_id: str
    summary: str | None = None
    diff: list[dict[str, Any]] | dict[str, Any] | None = None
    metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias="context",
        serialization_alias="metadata",
    )
    occurred_at: datetime
    recorded_at: datetime
