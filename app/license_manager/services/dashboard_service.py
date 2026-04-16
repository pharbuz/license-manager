from __future__ import annotations

from asyncio import gather
from datetime import UTC, datetime, timedelta

from fastapi import FastAPI

from app.license_manager.services.base_service import BaseService
from app.license_manager.services.healthcheck_service import HealthCheckService
from app.license_manager.services.models.dashboard import (
    DashboardDto,
    DashboardMetricsDto,
    DashboardServiceStateDto,
)
from app.license_manager.uow import UnitOfWork


class DashboardService(BaseService):
    def __init__(self, uow: UnitOfWork, app: FastAPI) -> None:
        super().__init__(uow)
        self._app = app

    async def get_dashboard(self) -> DashboardDto:
        reference_time = datetime.now(tz=UTC).replace(tzinfo=None)
        expiring_threshold = reference_time + timedelta(days=30)

        (
            health,
            active_licenses,
            archived_licenses,
            expiring_soon_licenses,
            expired_licenses,
            customers,
            products,
            license_kinds,
            app_packages,
            audit_events,
            latest_audit_at,
        ) = await gather(
            HealthCheckService(self._app).get_health(),
            self.uow.licenses.count_active_for_dashboard(),
            self.uow.licenses.count_archived_for_dashboard(),
            self.uow.licenses.count_expiring_soon_for_dashboard(
                reference_time,
                expiring_threshold,
            ),
            self.uow.licenses.count_expired_for_dashboard(reference_time),
            self.uow.customers.count_for_dashboard(),
            self.uow.products.count_for_dashboard(),
            self.uow.kinds.count_for_dashboard(),
            self.uow.app_packages.count_for_dashboard(),
            self.uow.audit_logs.count_for_dashboard(),
            self.uow.audit_logs.get_latest_occurred_at_for_dashboard(),
        )

        attention: list[str] = []
        if health.status != "ok":
            attention.append("One or more infrastructure dependencies are degraded.")
        if expired_licenses > 0:
            attention.append(f"{expired_licenses} active license(s) already expired.")
        if expiring_soon_licenses > 0:
            attention.append(
                f"{expiring_soon_licenses} license(s) will expire within the next 30 days."
            )

        return DashboardDto(
            health=health,
            metrics=DashboardMetricsDto(
                active_licenses=active_licenses,
                archived_licenses=archived_licenses,
                expiring_soon_licenses=expiring_soon_licenses,
                expired_licenses=expired_licenses,
                customers=customers,
                products=products,
                license_kinds=license_kinds,
                app_packages=app_packages,
                audit_events=audit_events,
            ),
            service_states=[
                DashboardServiceStateDto(
                    name="PostgreSQL",
                    status=health.services.postgres,
                ),
                DashboardServiceStateDto(
                    name="Key Vault",
                    status=health.services.key_vault,
                ),
            ],
            attention=attention,
            latest_audit_at=latest_audit_at,
            refreshed_at=datetime.now(tz=UTC),
        )
