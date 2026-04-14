from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from app.license_manager.services.models.common import BaseCamelModel


class AuditActorType(StrEnum):
    USER = "user"
    SERVICE = "service"
    SYSTEM = "system"


class AuditLogCreate(BaseCamelModel):
    actor_id: str | None = None
    actor_type: AuditActorType = Field(default=AuditActorType.SYSTEM)
    actor_display_name: str | None = None
    source: str = Field(default="api")
    request_id: str | None = None
    action: str
    entity_type: str
    entity_id: str
    summary: str | None = None
    diff: list[dict[str, Any]] | dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
