from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, Index, Text, desc
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlmodel import Field

from app.license_manager.db.base import Base


class Setting(Base, table=True):
    __tablename__ = "settings"
    __table_args__ = (
        Index("settings_schema_scope_idx", "schema_id", "scope"),
        Index("settings_modified_at_idx", desc("modified_at")),
        Index(
            "settings_value_gin_idx",
            "value",
            postgresql_using="gin",
            postgresql_ops={"value": "jsonb_path_ops"},
        ),
        {"schema": "licensemanager"},
    )

    object_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            default=uuid.uuid4,
        )
    )
    schema_id: str = Field(sa_column=Column(Text, nullable=False))
    scope: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=False), nullable=False)
    )
    modified_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=False), nullable=True)
    )
    created_by: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    modified_by: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    value: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
