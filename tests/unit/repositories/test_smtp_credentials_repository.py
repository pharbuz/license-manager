from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pytest

from app.license_manager.repositories.smtp_credentials import SmtpCredentialRepository
from app.license_manager.services.models.smtp_credentials import (
    SmtpCredentialSecretPayload,
)


class FakeSecretClient:
    def __init__(self) -> None:
        self.stored: dict[str, str] = {}
        self.deleted: set[str] = set()

    def set_secret(self, name: str, value: str, **kwargs):
        self.stored[name] = value
        return SimpleNamespace(name=name, properties=SimpleNamespace(version="v1"))

    def get_secret(self, name: str):
        if name not in self.stored:
            from azure.core.exceptions import ResourceNotFoundError

            raise ResourceNotFoundError(message="not found")
        return SimpleNamespace(
            name=name,
            value=self.stored[name],
            properties=SimpleNamespace(version="v1"),
        )

    def begin_delete_secret(self, name: str):
        self.deleted.add(name)
        return SimpleNamespace(result=lambda: None)

    def purge_deleted_secret(self, name: str) -> None:
        self.deleted.discard(name)


@pytest.mark.asyncio
async def test_repository_store_and_fetch(monkeypatch) -> None:
    fake_client = FakeSecretClient()
    monkeypatch.setattr(
        "app.license_manager.repositories.smtp_credentials.get_settings",
        lambda: SimpleNamespace(
            AZURE_KEY_VAULT_URL="https://vault.example",
            SMTP_CREDENTIALS_SECRET_NAME="smtp-credentials",
            AZURE_TENANT_ID=None,
            AZURE_CLIENT_ID=None,
            AZURE_CLIENT_SECRET=None,
            AZURE_USE_CLI_CREDENTIAL=False,
        ),
    )

    repo = SmtpCredentialRepository(client=fake_client)
    payload = SmtpCredentialSecretPayload(
        host="smtp.example.com",
        port=587,
        username="user",
        password="secret",
        sender_email="sender@example.com",
        use_tls=True,
        use_ssl=False,
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )

    name, version = await repo.store(payload)
    assert name == "smtp-credentials"
    assert version == "v1"

    fetched_name, fetched_version, fetched = await repo.fetch()
    assert fetched_name == "smtp-credentials"
    assert fetched_version == "v1"
    assert fetched.host == "smtp.example.com"
