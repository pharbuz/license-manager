from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlmodel import Field

from app.license_manager.db.base import Base


class License(Base, table=True):
    __tablename__ = "licenses"
    __table_args__ = (
        UniqueConstraint("license_key", name="licensekey_unique"),
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
    customer_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("licensemanager.customers.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
    )
    product_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("licensemanager.products.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
    )
    kind_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("licensemanager.kinds.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
    )
    license_count: int = Field(sa_column=Column(Integer, nullable=False))
    license_state: str = Field(sa_column=Column(String(128), nullable=False))
    license_key: str = Field(sa_column=Column(String(512), nullable=False))
    license_email: str = Field(sa_column=Column(Text, nullable=False))
    double_send: bool = Field(sa_column=Column(Boolean(), nullable=False))
    begin_date: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=False), nullable=False)
    )
    end_date: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=False), nullable=False)
    )
    notification_date: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=False), nullable=False)
    )
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
