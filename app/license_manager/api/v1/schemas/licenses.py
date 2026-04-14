from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from app.license_manager.api.v1.schemas.common import BaseCamelSchema


class LicenseGenerateQuerySchema(BaseCamelSchema):
    customer_symbol: str = Field(default="")
    end_date: datetime = Field(default_factory=datetime.utcnow)
    license_count: int = Field(default=1, ge=1, le=9999)


class LicenseGeneratedKeySchema(BaseCamelSchema):
    license_key: str


class LicenseSchema(BaseCamelSchema):
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


class LicenseCreateSchema(BaseCamelSchema):
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


class LicenseUpdateSchema(BaseCamelSchema):
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
