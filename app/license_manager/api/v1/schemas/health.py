from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.license_manager.api.v1.schemas.common import BaseCamelSchema


class HealthServicesOut(BaseCamelSchema):
    postgres: Literal["ok", "error"]
    key_vault: Literal["ok", "error"]


class HealthOut(BaseCamelSchema):
    status: Literal["ok", "degraded"]
    services: HealthServicesOut
    errors: dict[str, str] = Field(default_factory=dict)
