from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlmodel import Field

from app.license_manager.db.base import Base


class Customer(Base, table=True):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("customer_symbol", name="customersymbol_unique"),
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
    name: str = Field(sa_column=Column(String(128), nullable=False))
    contact_person_name: str | None = Field(
        default=None,
        sa_column=Column(String(128), nullable=True),
    )
    contact_person_phone: str | None = Field(
        default=None,
        sa_column=Column(String(128), nullable=True),
    )
    email: str = Field(sa_column=Column(String(128), nullable=False))
    notifications_enabled: bool = Field(
        sa_column=Column(
            Boolean(),
            nullable=False,
            server_default=text("true"),
        )
    )
    gem_fury_used: bool = Field(
        sa_column=Column(
            Boolean(),
            nullable=False,
            server_default=text("true"),
        )
    )
    customer_symbol: str = Field(sa_column=Column(String(3), nullable=False))
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
