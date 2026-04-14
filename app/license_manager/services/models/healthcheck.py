from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from app.license_manager.services.models.common import BaseCamelModel


class HealthOverallStatus(StrEnum):
    OK = "ok"
    DEGRADED = "degraded"


class HealthServiceStatus(StrEnum):
    OK = "ok"
    ERROR = "error"


class HealthServicesModel(BaseCamelModel):
    postgres: HealthServiceStatus
    key_vault: HealthServiceStatus


class HealthCheckModel(BaseCamelModel):
    status: HealthOverallStatus
    services: HealthServicesModel
    errors: dict[str, str] = Field(default_factory=dict)
