from __future__ import annotations

from uuid import UUID

from pydantic import field_validator

from app.license_manager.api.v1.schemas.common import BaseCamelSchema
from app.license_manager.services.models.dropdowns import DropdownType


class DropdownQuerySchema(BaseCamelSchema):
    type: DropdownType

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        normalized = value.strip().lower().replace("-", " ").replace("_", " ")
        if normalized == "kind":
            normalized = DropdownType.LICENSE_KIND.value
        return normalized


class DropdownItemSchema(BaseCamelSchema):
    id: UUID
    text: str
