from __future__ import annotations

from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.license_manager.api.main import create_app
from app.license_manager.middleware.problem_details import ProblemDetailsMiddleware
from app.license_manager.middleware.request_id import RequestIDMiddleware
from app.license_manager.middleware.timing import TimingMiddleware
from app.license_manager.services.models.healthcheck import (
    HealthCheckModel,
    HealthOverallStatus,
    HealthServicesModel,
    HealthServiceStatus,
)


class _Settings:
    APP_NAME = "License Manager API"
    VERSION = "1.0.0"
    CORS_ALLOWED_ORIGINS = ["*"]
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOWED_METHODS = ["*"]
    CORS_ALLOWED_HEADERS = ["*"]
    KEYCLOAK_BASE_URL = "http://example.com"
    KEYCLOAK_REALM = "test"
    KEYCLOAK_VERIFY_SSL = False
    KEYCLOAK_CLIENT_ID = "client-id"
    KEYCLOAK_CLIENT_SECRET = "client-secret"
    KEYCLOAK_ADMIN_SECRET = "admin-secret"
    KEYCLOAK_CALLBACK_URI = "http://localhost:8000/docs/oauth2-redirect.html"


def test_create_app_registers_middlewares(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.license_manager.api.main.get_settings", lambda: _Settings()
    )

    app = create_app()

    middleware_types = {middleware.cls for middleware in app.user_middleware}

    assert RequestIDMiddleware in middleware_types
    assert ProblemDetailsMiddleware in middleware_types
    assert TimingMiddleware in middleware_types
    assert CORSMiddleware in middleware_types
    assert app.title == "License Manager API"
    assert app.version == "1.0.0"
    assert app.openapi_url is None
    assert app.docs_url is None
    assert app.redoc_url is None

    openapi_schema = app.openapi()
    assert openapi_schema["tags"]
    assert "OAuth2" in openapi_schema["components"]["securitySchemes"]
    assert any(tag["name"] == "SMTP Credentials" for tag in openapi_schema["tags"])


def test_health_endpoint_returns_200_when_all_dependencies_are_ok(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.license_manager.api.main.get_settings", lambda: _Settings()
    )
    app = create_app()

    async def _healthy(self: object) -> HealthCheckModel:
        return HealthCheckModel(
            status=HealthOverallStatus.OK,
            services=HealthServicesModel(
                postgres=HealthServiceStatus.OK,
                key_vault=HealthServiceStatus.OK,
            ),
            errors={},
        )

    monkeypatch.setattr(
        "app.license_manager.api.main.HealthCheckService.get_health", _healthy
    )

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "services": {
            "postgres": "ok",
            "keyVault": "ok",
        },
        "errors": {},
    }


def test_health_endpoint_returns_503_when_dependency_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.license_manager.api.main.get_settings", lambda: _Settings()
    )
    app = create_app()

    async def _degraded(self: object) -> HealthCheckModel:
        return HealthCheckModel(
            status=HealthOverallStatus.DEGRADED,
            services=HealthServicesModel(
                postgres=HealthServiceStatus.ERROR,
                key_vault=HealthServiceStatus.OK,
            ),
            errors={"postgres": "connection refused"},
        )

    monkeypatch.setattr(
        "app.license_manager.api.main.HealthCheckService.get_health", _degraded
    )

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "services": {
            "postgres": "error",
            "keyVault": "ok",
        },
        "errors": {"postgres": "connection refused"},
    }
