from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI

from app.license_manager.services.healthcheck_service import HealthCheckService


class _DummySettings:
    AZURE_KEY_VAULT_URL = "https://example.vault.azure.net/"


class _SecretNotFoundClient:
    def get_secret(self, name: str) -> None:
        raise Exception("(SecretNotFound) Secret not found")


class _RecordingClient:
    def __init__(self) -> None:
        self.requested_name: str | None = None

    def get_secret(self, name: str) -> None:
        self.requested_name = name
        raise Exception("(SecretNotFound) Secret not found")


@pytest.mark.asyncio
async def test_key_vault_health_returns_ok_for_missing_probe_secret(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.license_manager.services.healthcheck_service.get_settings",
        lambda: _DummySettings(),
    )
    monkeypatch.setattr(
        "app.license_manager.services.healthcheck_service.SmtpCredentialRepository",
        lambda: SimpleNamespace(client=_SecretNotFoundClient()),
    )

    service = HealthCheckService(FastAPI())

    healthy, error = await service._check_key_vault_health()

    assert healthy is True
    assert error is None


@pytest.mark.asyncio
async def test_key_vault_health_uses_valid_probe_secret_name(monkeypatch) -> None:
    recording_client = _RecordingClient()

    monkeypatch.setattr(
        "app.license_manager.services.healthcheck_service.get_settings",
        lambda: _DummySettings(),
    )
    monkeypatch.setattr(
        "app.license_manager.services.healthcheck_service.SmtpCredentialRepository",
        lambda: SimpleNamespace(client=recording_client),
    )

    service = HealthCheckService(FastAPI())

    healthy, error = await service._check_key_vault_health()

    assert healthy is True
    assert error is None
    assert recording_client.requested_name == "license-manager-healthcheck-probe"
    assert "_" not in recording_client.requested_name
