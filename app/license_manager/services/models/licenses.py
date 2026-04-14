from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from app.license_manager.services.models.common import BaseCamelModel


class LicenseDto(BaseCamelModel):
    id: UUID
    customer_id: UUID | None = Field(default=None)
    product_id: UUID | None = Field(default=None)
    kind_id: UUID | None = Field(default=None)
    license_count: int
    license_state: str
    license_key: str
    license_email: EmailStr
    double_send: bool
    begin_date: datetime
    end_date: datetime
    notification_date: datetime
    created_at: datetime
    modified_at: datetime


class LicenseCreateDto(BaseCamelModel):
    customer_id: UUID | None = Field(default=None)
    product_id: UUID | None = Field(default=None)
    kind_id: UUID | None = Field(default=None)
    license_count: int
    license_state: str
    license_key: str
    license_email: EmailStr
    double_send: bool = False
    begin_date: datetime
    end_date: datetime
    notification_date: datetime


class LicenseUpdateDto(BaseCamelModel):
    customer_id: UUID | None = Field(default=None)
    product_id: UUID | None = Field(default=None)
    kind_id: UUID | None = Field(default=None)
    license_count: int | None = Field(default=None)
    license_state: str | None = Field(default=None)
    license_key: str | None = Field(default=None)
    license_email: EmailStr | None = Field(default=None)
    double_send: bool | None = Field(default=None)
    begin_date: datetime | None = Field(default=None)
    end_date: datetime | None = Field(default=None)
    notification_date: datetime | None = Field(default=None)
