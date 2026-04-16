from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.license_manager.api.v1.schemas.common import BaseCamelSchema
from app.license_manager.api.v1.schemas.health import HealthOut


class DashboardMetricsSchema(BaseCamelSchema):
    active_licenses: int
    archived_licenses: int
    expiring_soon_licenses: int
    expired_licenses: int
    customers: int
    products: int
    license_kinds: int
    app_packages: int
    audit_events: int


class DashboardServiceStateSchema(BaseCamelSchema):
    name: str
    status: Literal["ok", "error"]


class DashboardSchema(BaseCamelSchema):
    health: HealthOut
    metrics: DashboardMetricsSchema
    service_states: list[DashboardServiceStateSchema]
    attention: list[str] = Field(default_factory=list)
    latest_audit_at: datetime | None = Field(default=None)
    refreshed_at: datetime
