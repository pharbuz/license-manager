from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.license_manager.services.models.common import BaseCamelModel


class AppPackageDto(BaseCamelModel):
    id: UUID
    version_number: str
    binary_name: str
    gem_fury_url: str
    binary_url: str
    created_at: datetime
    modified_at: datetime


class AppPackageCreateDto(BaseCamelModel):
    version_number: str
    binary_name: str
    gem_fury_url: str
    binary_url: str


class AppPackageUpdateDto(BaseCamelModel):
    version_number: str | None = Field(default=None)
    binary_name: str | None = Field(default=None)
    gem_fury_url: str | None = Field(default=None)
    binary_url: str | None = Field(default=None)
