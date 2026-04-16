from __future__ import annotations

from datetime import datetime

from app.license_manager.services.models.common import BaseCamelModel
from app.license_manager.services.models.healthcheck import (
    HealthCheckModel,
    HealthServiceStatus,
)


class DashboardMetricsDto(BaseCamelModel):
    active_licenses: int
    archived_licenses: int
    expiring_soon_licenses: int
    expired_licenses: int
    customers: int
    products: int
    license_kinds: int
    app_packages: int
    audit_events: int


class DashboardServiceStateDto(BaseCamelModel):
    name: str
    status: HealthServiceStatus


class DashboardDto(BaseCamelModel):
    health: HealthCheckModel
    metrics: DashboardMetricsDto
    service_states: list[DashboardServiceStateDto]
    attention: list[str]
    latest_audit_at: datetime | None
    refreshed_at: datetime
