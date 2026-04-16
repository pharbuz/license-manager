from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI

from app.license_manager.services.dashboard_service import DashboardService
from app.license_manager.services.models.healthcheck import (
    HealthCheckModel,
    HealthOverallStatus,
    HealthServicesModel,
    HealthServiceStatus,
)


class FakeDashboardUnitOfWork:
    def __init__(self) -> None:
        self.licenses = MagicMock()
        self.licenses.count_active_for_dashboard = AsyncMock(return_value=5)
        self.licenses.count_archived_for_dashboard = AsyncMock(return_value=2)
        self.licenses.count_expiring_soon_for_dashboard = AsyncMock(return_value=1)
        self.licenses.count_expired_for_dashboard = AsyncMock(return_value=3)

        self.customers = MagicMock()
        self.customers.count_for_dashboard = AsyncMock(return_value=4)

        self.products = MagicMock()
        self.products.count_for_dashboard = AsyncMock(return_value=6)

        self.kinds = MagicMock()
        self.kinds.count_for_dashboard = AsyncMock(return_value=7)

        self.app_packages = MagicMock()
        self.app_packages.count_for_dashboard = AsyncMock(return_value=8)

        self.audit_logs = MagicMock()
        self.audit_logs.count_for_dashboard = AsyncMock(return_value=9)
        self.audit_logs.get_latest_occurred_at_for_dashboard = AsyncMock(
            return_value=datetime(2026, 4, 16, 10, 0, tzinfo=UTC)
        )


@pytest.mark.asyncio
async def test_dashboard_service_aggregates_metrics_and_attention(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _health(*_args, **_kwargs) -> HealthCheckModel:
        return HealthCheckModel(
            status=HealthOverallStatus.DEGRADED,
            services=HealthServicesModel(
                postgres=HealthServiceStatus.ERROR,
                key_vault=HealthServiceStatus.OK,
            ),
            errors={"postgres": "connection refused"},
        )

    monkeypatch.setattr(
        "app.license_manager.services.dashboard_service.HealthCheckService",
        lambda _app: SimpleNamespace(get_health=_health),
    )

    service = DashboardService(FakeDashboardUnitOfWork(), FastAPI())

    result = await service.get_dashboard()

    assert result.metrics.active_licenses == 5
    assert result.metrics.license_kinds == 7
    assert result.metrics.audit_events == 9
    assert result.service_states[0].name == "PostgreSQL"
    assert result.service_states[0].status == HealthServiceStatus.ERROR
    assert result.latest_audit_at == datetime(2026, 4, 16, 10, 0, tzinfo=UTC)
    assert "One or more infrastructure dependencies are degraded." in result.attention
    assert "3 active license(s) already expired." in result.attention
    assert "1 license(s) will expire within the next 30 days." in result.attention
