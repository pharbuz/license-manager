from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from app.license_manager.services.models.common import BaseCamelModel


class DropdownType(StrEnum):
    CUSTOMER = "customer"
    LICENSE_KIND = "license kind"
    PRODUCT = "product"


class DropdownItemDto(BaseCamelModel):
    id: UUID
    text: str
