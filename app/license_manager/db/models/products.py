from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlmodel import Field

from app.license_manager.db.base import Base


class Product(Base, table=True):
    __tablename__ = "products"
    __table_args__ = ({"schema": "licensemanager"},)

    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            default=uuid.uuid4,
        )
    )
    name: str = Field(sa_column=Column(String(128), nullable=False))
    kind: str = Field(sa_column=Column(Text, nullable=False))
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
