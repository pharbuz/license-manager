from __future__ import annotations

import asyncio
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


@pytest.mark.asyncio
async def test_dashboard_service_does_not_run_repository_calls_concurrently(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _health(*_args, **_kwargs) -> HealthCheckModel:
        return HealthCheckModel(
            status=HealthOverallStatus.OK,
            services=HealthServicesModel(
                postgres=HealthServiceStatus.OK,
                key_vault=HealthServiceStatus.OK,
            ),
            errors={},
        )

    monkeypatch.setattr(
        "app.license_manager.services.dashboard_service.HealthCheckService",
        lambda _app: SimpleNamespace(get_health=_health),
    )

    active_calls = 0

    async def _sequential(value: int | datetime) -> int | datetime:
        nonlocal active_calls
        if active_calls:
            raise AssertionError("dashboard repository calls must not overlap")
        active_calls += 1
        try:
            await asyncio.sleep(0)
            return value
        finally:
            active_calls -= 1

    async def _active_licenses() -> int:
        return await _sequential(5)

    async def _archived_licenses() -> int:
        return await _sequential(2)

    async def _expiring_soon(*_args: object) -> int:
        return await _sequential(1)

    async def _expired(*_args: object) -> int:
        return await _sequential(3)

    async def _customers() -> int:
        return await _sequential(4)

    async def _products() -> int:
        return await _sequential(6)

    async def _kinds() -> int:
        return await _sequential(7)

    async def _app_packages() -> int:
        return await _sequential(8)

    async def _audit_events() -> int:
        return await _sequential(9)

    async def _latest_audit_at() -> datetime:
        return await _sequential(datetime(2026, 4, 16, 10, 0, tzinfo=UTC))

    fake_uow = SimpleNamespace(
        licenses=SimpleNamespace(
            count_active_for_dashboard=AsyncMock(side_effect=_active_licenses),
            count_archived_for_dashboard=AsyncMock(side_effect=_archived_licenses),
            count_expiring_soon_for_dashboard=AsyncMock(side_effect=_expiring_soon),
            count_expired_for_dashboard=AsyncMock(side_effect=_expired),
        ),
        customers=SimpleNamespace(
            count_for_dashboard=AsyncMock(side_effect=_customers)
        ),
        products=SimpleNamespace(count_for_dashboard=AsyncMock(side_effect=_products)),
        kinds=SimpleNamespace(count_for_dashboard=AsyncMock(side_effect=_kinds)),
        app_packages=SimpleNamespace(
            count_for_dashboard=AsyncMock(side_effect=_app_packages)
        ),
        audit_logs=SimpleNamespace(
            count_for_dashboard=AsyncMock(side_effect=_audit_events),
            get_latest_occurred_at_for_dashboard=AsyncMock(
                side_effect=_latest_audit_at
            ),
        ),
    )

    service = DashboardService(fake_uow, FastAPI())

    result = await service.get_dashboard()

    assert result.metrics.active_licenses == 5
    assert result.metrics.audit_events == 9
