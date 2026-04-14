from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from app.license_manager.services.models.common import BaseCamelModel


class CustomerDto(BaseCamelModel):
    id: UUID
    name: str
    contact_person_name: str | None = Field(default=None)
    contact_person_phone: str | None = Field(default=None)
    email: EmailStr
    notifications_enabled: bool
    gem_fury_used: bool
    customer_symbol: str
    created_at: datetime
    modified_at: datetime


class CustomerCreateDto(BaseCamelModel):
    name: str
    email: EmailStr
    customer_symbol: str
    notifications_enabled: bool = True
    gem_fury_used: bool = True
    contact_person_name: str | None = Field(default=None)
    contact_person_phone: str | None = Field(default=None)


class CustomerUpdateDto(BaseCamelModel):
    name: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    customer_symbol: str | None = Field(default=None)
    notifications_enabled: bool | None = Field(default=None)
    gem_fury_used: bool | None = Field(default=None)
    contact_person_name: str | None = Field(default=None)
    contact_person_phone: str | None = Field(default=None)
