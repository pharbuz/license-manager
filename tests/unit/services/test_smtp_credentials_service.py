from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.license_manager.services.models.smtp_credentials import (
    SmtpCredentialCreateDto,
    SmtpCredentialSecretPayload,
    SmtpCredentialUpdateDto,
)
from app.license_manager.services.smtp_credentials_service import SmtpCredentialService


class FakeRepository:
    def __init__(self) -> None:
        self.store = AsyncMock(return_value=("smtp-credentials", "v2"))
        self.fetch = AsyncMock(
            return_value=(
                "smtp-credentials",
                "v1",
                SmtpCredentialSecretPayload(
                    host="smtp.example.com",
                    port=587,
                    username="user",
                    password="secret",
                    sender_email="sender@example.com",
                    use_tls=True,
                    use_ssl=False,
                    created_at=datetime(2026, 1, 1, 0, 0, 0),
                    modified_at=datetime(2026, 1, 1, 0, 0, 0),
                ),
            )
        )
        self.delete = AsyncMock(return_value=None)


@pytest.mark.asyncio
async def test_service_create_credentials() -> None:
    repo = FakeRepository()
    service = SmtpCredentialService(repository=repo)

    result = await service.create_smtp_credentials(
        SmtpCredentialCreateDto(
            host="smtp.example.com",
            port=587,
            username="user",
            password="secret",
            sender_email="sender@example.com",
        )
    )

    assert result.secret_name == "smtp-credentials"
    assert result.secret_version == "v2"
    assert result.host == "smtp.example.com"
    repo.store.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_update_credentials() -> None:
    repo = FakeRepository()
    service = SmtpCredentialService(repository=repo)

    result = await service.update_smtp_credentials(
        SmtpCredentialUpdateDto(password="new-secret")
    )

    assert result.secret_name == "smtp-credentials"
    assert result.secret_version == "v2"
    repo.fetch.assert_awaited_once()
    repo.store.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_delete_credentials() -> None:
    repo = FakeRepository()
    service = SmtpCredentialService(repository=repo)

    await service.delete_smtp_credentials()

    repo.delete.assert_awaited_once_with(purge=True)
