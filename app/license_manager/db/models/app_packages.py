from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlmodel import Field

from app.license_manager.db.base import Base


class AppPackage(Base, table=True):
    __tablename__ = "app_packages"
    __table_args__ = (
        UniqueConstraint("version_number", name="versionnumber_unique"),
        {"schema": "licensemanager"},
    )

    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            default=uuid.uuid4,
        )
    )
    version_number: str = Field(sa_column=Column(String(16), nullable=False))
    binary_name: str = Field(sa_column=Column(String(128), nullable=False))
    gem_fury_url: str = Field(sa_column=Column(String(128), nullable=False))
    binary_url: str = Field(sa_column=Column(String(128), nullable=False))
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    modified_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )
