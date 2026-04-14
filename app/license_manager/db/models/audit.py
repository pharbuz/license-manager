from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Column, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlmodel import Field

from app.license_manager.db.base import Base


class AuditLogEntry(Base, table=True):
    __tablename__ = "audit_log_entries"
    __table_args__ = (
        Index("ix_audit_log_entries_created_at", "recorded_at"),
        Index("ix_audit_log_entries_entity", "entity_type", "entity_id"),
        {"schema": "licensemanager"},
    )

    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
        )
    )
    actor_id: str | None = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )
    actor_type: str = Field(
        default="system",
        sa_column=Column(String(64), nullable=False, server_default="system"),
    )
    actor_display_name: str | None = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )
    source: str = Field(
        default="api",
        sa_column=Column(String(64), nullable=False, server_default="api"),
    )
    request_id: str | None = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )
    action: str = Field(sa_column=Column(String(128), nullable=False))
    entity_type: str = Field(sa_column=Column(String(255), nullable=False))
    entity_id: str = Field(sa_column=Column(String(255), nullable=False))
    summary: str | None = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )
    diff: list[dict[str, Any]] | dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
    )
    context: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column("metadata", JSONB, nullable=True),
    )
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    recorded_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
