from __future__ import annotations

from types import SimpleNamespace

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.license_manager.api.main import create_app


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


class FakeKeycloak:
    def __init__(self, *args, **kwargs):
        pass

    def add_swagger_config(self, app):
        return None

    def get_current_user(self, *args, **kwargs):
        def _auth(token, *args, **kwargs):
            if token != "admin-token":
                raise HTTPException(status_code=401, detail="Unauthorized")
            return SimpleNamespace(roles=["app.admin"], extra_fields={})

        return _auth

    @property
    def user_auth_scheme(self):
        async def _auth(*args, **kwargs):
            raise HTTPException(status_code=401, detail="Unauthorized")

        return _auth


def test_openapi_spec_requires_auth(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.license_manager.api.main.get_settings", lambda: _Settings()
    )
    monkeypatch.setattr("app.license_manager.api.main.FastAPIKeycloak", FakeKeycloak)

    app = create_app()
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 401


def test_openapi_spec_accepts_docs_token_cookie(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.license_manager.api.main.get_settings", lambda: _Settings()
    )
    monkeypatch.setattr("app.license_manager.api.main.FastAPIKeycloak", FakeKeycloak)

    app = create_app()
    client = TestClient(app)

    response = client.get("/openapi.json", cookies={"docs_token": "admin-token"})

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "License Manager API"


def test_swagger_ui_redirects_without_token(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.license_manager.api.main.get_settings", lambda: _Settings()
    )
    monkeypatch.setattr("app.license_manager.api.main.FastAPIKeycloak", FakeKeycloak)

    app = create_app()
    client = TestClient(app)

    response = client.get("/docs/swagger", follow_redirects=False)

    assert response.status_code == 302
    assert "/docs/login" in response.headers["location"]
