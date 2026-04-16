from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.license_manager.api.dependencies import get_uow
from app.license_manager.api.v1.routers import dashboard_router, dropdown_router
from app.license_manager.services.models.healthcheck import (
    HealthCheckModel,
    HealthOverallStatus,
    HealthServicesModel,
    HealthServiceStatus,
)


def test_dropdown_endpoint_returns_customer_items() -> None:
    customer_id = uuid4()
    fake_uow = SimpleNamespace(
        customers=SimpleNamespace(
            list_dropdown_items=AsyncMock(
                return_value=[(customer_id, "ACM", "Acme Corporation")]
            )
        ),
        kinds=SimpleNamespace(list_dropdown_items=AsyncMock(return_value=[])),
        products=SimpleNamespace(list_dropdown_items=AsyncMock(return_value=[])),
    )

    app = FastAPI()

    async def _override_get_uow():
        yield fake_uow

    app.dependency_overrides[get_uow] = _override_get_uow
    app.include_router(dropdown_router)
    client = TestClient(app)

    response = client.get("/dropdown", params={"type": "customer"})

    assert response.status_code == 200
    assert response.json() == [
        {"id": str(customer_id), "text": "ACM - Acme Corporation"}
    ]


def test_dropdown_endpoint_accepts_license_kind_alias() -> None:
    kind_id = uuid4()
    fake_uow = SimpleNamespace(
        customers=SimpleNamespace(list_dropdown_items=AsyncMock(return_value=[])),
        kinds=SimpleNamespace(
            list_dropdown_items=AsyncMock(return_value=[(kind_id, "Trial")])
        ),
        products=SimpleNamespace(list_dropdown_items=AsyncMock(return_value=[])),
    )

    app = FastAPI()

    async def _override_get_uow():
        yield fake_uow

    app.dependency_overrides[get_uow] = _override_get_uow
    app.include_router(dropdown_router)
    client = TestClient(app)

    response = client.get("/dropdown", params={"type": "license_kind"})

    assert response.status_code == 200
    assert response.json() == [{"id": str(kind_id), "text": "Trial"}]


def test_dashboard_endpoint_returns_aggregated_payload(
    monkeypatch,
) -> None:
    health_payload = HealthCheckModel(
        status=HealthOverallStatus.OK,
        services=HealthServicesModel(
            postgres=HealthServiceStatus.OK,
            key_vault=HealthServiceStatus.ERROR,
        ),
        errors={"keyVault": "access denied"},
    )

    fake_uow = SimpleNamespace(
        licenses=SimpleNamespace(
            count_active_for_dashboard=AsyncMock(return_value=12),
            count_archived_for_dashboard=AsyncMock(return_value=3),
            count_expiring_soon_for_dashboard=AsyncMock(return_value=2),
            count_expired_for_dashboard=AsyncMock(return_value=1),
        ),
        customers=SimpleNamespace(count_for_dashboard=AsyncMock(return_value=4)),
        products=SimpleNamespace(count_for_dashboard=AsyncMock(return_value=5)),
        kinds=SimpleNamespace(count_for_dashboard=AsyncMock(return_value=6)),
        app_packages=SimpleNamespace(count_for_dashboard=AsyncMock(return_value=7)),
        audit_logs=SimpleNamespace(
            count_for_dashboard=AsyncMock(return_value=8),
            get_latest_occurred_at_for_dashboard=AsyncMock(
                return_value=datetime(2026, 4, 17, 8, 30, tzinfo=UTC)
            ),
        ),
    )

    monkeypatch.setattr(
        "app.license_manager.services.dashboard_service.HealthCheckService",
        lambda _app: SimpleNamespace(get_health=AsyncMock(return_value=health_payload)),
    )

    app = FastAPI()

    async def _override_get_uow():
        yield fake_uow

    app.dependency_overrides[get_uow] = _override_get_uow
    app.include_router(dashboard_router)
    client = TestClient(app)

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert response.json()["metrics"] == {
        "activeLicenses": 12,
        "archivedLicenses": 3,
        "expiringSoonLicenses": 2,
        "expiredLicenses": 1,
        "customers": 4,
        "products": 5,
        "licenseKinds": 6,
        "appPackages": 7,
        "auditEvents": 8,
    }
    assert response.json()["serviceStates"] == [
        {"name": "PostgreSQL", "status": "ok"},
        {"name": "Key Vault", "status": "error"},
    ]
    assert response.json()["latestAuditAt"] == "2026-04-17T08:30:00Z"
