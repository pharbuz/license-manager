from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.license_manager.api.v1.routers import smtp_credentials as smtp_router


class FakeService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def get_smtp_credentials(self):
        self.calls.append("get")
        return SimpleNamespace(
            secret_name="smtp-credentials",
            secret_version="v1",
            host="smtp.example.com",
            port=587,
            username="user",
            sender_email="sender@example.com",
            use_tls=True,
            use_ssl=False,
            created_at=datetime(2026, 1, 1, 0, 0, 0),
            modified_at=datetime(2026, 1, 1, 0, 0, 0),
        )

    async def create_smtp_credentials(self, payload):
        self.calls.append("create")
        return await self.get_smtp_credentials()

    async def update_smtp_credentials(self, payload):
        self.calls.append("update")
        return await self.get_smtp_credentials()

    async def delete_smtp_credentials(self, *, purge: bool = True):
        self.calls.append("delete")


def _client(fake_service: FakeService, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    app = FastAPI()
    monkeypatch.setattr(smtp_router, "SmtpCredentialService", lambda: fake_service)
    app.include_router(smtp_router.router)
    return TestClient(app)


def test_get_smtp_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeService()
    client = _client(fake, monkeypatch)

    response = client.get("/smtp-credentials")

    assert response.status_code == 200
    assert response.json()["secretName"] == "smtp-credentials"
    assert fake.calls == ["get"]


def test_create_smtp_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeService()
    client = _client(fake, monkeypatch)

    response = client.post(
        "/smtp-credentials",
        json={
            "host": "smtp.example.com",
            "port": 587,
            "username": "user",
            "password": "secret",
        },
    )

    assert response.status_code == 201
    assert fake.calls[0] == "create"
