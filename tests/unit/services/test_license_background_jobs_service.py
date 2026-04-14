from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.license_manager.db.models import Customer, License, Product
from app.license_manager.services.license_background_jobs_service import (
    LicenseBackgroundJobsService,
)
from app.license_manager.services.models.background_jobs import (
    LicenseArchiverTaskPayload,
    LicenseCheckTaskPayload,
)
from app.license_manager.services.models.smtp_credentials import (
    SmtpCredentialSecretPayload,
)


def test_build_license_expiration_subject() -> None:
    assert (
        LicenseBackgroundJobsService._build_license_expiration_subject("AppPackage")
        == "Application Package license"
    )
    assert (
        LicenseBackgroundJobsService._build_license_expiration_subject("Java")
        == "Java license"
    )


def test_build_license_expiration_text_body() -> None:
    body = LicenseBackgroundJobsService._build_license_expiration_text_body(
        person_name="Dear John",
        customer_name="Acme",
        product_name="AppPackage",
        days_to_expire=7,
        expiration_date="20.04.2026",
        license_key="LIC-123",
    )

    assert "Dear John" in body
    assert "Acme" in body
    assert "AppPackage" in body
    assert "7 days" in body
    assert "20.04.2026" in body
    assert "LIC-123" in body


def test_build_receivers() -> None:
    assert LicenseBackgroundJobsService._build_receivers(
        license_email="license@example.com",
        customer_email="customer@example.com",
        double_send=True,
    ) == ["license@example.com", "customer@example.com"]

    assert LicenseBackgroundJobsService._build_receivers(
        license_email="license@example.com",
        customer_email="customer@example.com",
        double_send=False,
    ) == ["license@example.com"]


@pytest.fixture
def smtp_payload() -> SmtpCredentialSecretPayload:
    return SmtpCredentialSecretPayload.model_validate(
        {
            "host": "smtp.example.com",
            "port": 587,
            "username": "user@example.com",
            "password": "secret",
            "senderEmail": "sender@example.com",
            "useTls": True,
            "useSsl": False,
            "createdAt": "2026-01-01T00:00:00Z",
            "modifiedAt": "2026-01-01T00:00:00Z",
        }
    )


@pytest.mark.asyncio
async def test_check_license_expirations_uses_repository_and_commits(
    monkeypatch: pytest.MonkeyPatch,
    smtp_payload: SmtpCredentialSecretPayload,
) -> None:
    license_entity = License(
        id=uuid4(),
        customer_id=uuid4(),
        product_id=uuid4(),
        kind_id=None,
        license_count=1,
        license_state="Active",
        license_key="LIC-123",
        license_email="owner@example.com",
        double_send=False,
        begin_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 1, 31),
        notification_date=datetime(1970, 1, 1),
    )
    customer_entity = Customer(
        id=uuid4(),
        name="Acme",
        contact_person_name="John Doe",
        email="customer@example.com",
        notifications_enabled=True,
        gem_fury_used=True,
        customer_symbol="ACM",
    )
    product_entity = Product(
        id=uuid4(),
        name="AppPackage",
        kind="Agent",
    )
    licenses_repository = SimpleNamespace(
        list_expiring_with_customer_and_product=AsyncMock(
            return_value=[(license_entity, customer_entity, product_entity)]
        ),
        save=AsyncMock(return_value=license_entity),
    )
    uow = SimpleNamespace(licenses=licenses_repository, commit=AsyncMock())
    service = LicenseBackgroundJobsService(uow)

    monkeypatch.setattr(
        service, "_fetch_smtp_credentials", AsyncMock(return_value=smtp_payload)
    )
    send_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "app.license_manager.services.email_service.EmailService.send_notification",
        send_mock,
    )

    result = await service.check_license_expirations(
        LicenseCheckTaskPayload(days_from_today_to_check=[1])
    )

    assert result.notifications_sent == 1
    licenses_repository.save.assert_awaited_once_with(license_entity)
    uow.commit.assert_awaited_once()
    send_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_archive_expired_licenses_uses_repository_and_commits() -> None:
    licenses_repository = SimpleNamespace(archive_expired=AsyncMock(return_value=3))
    uow = SimpleNamespace(licenses=licenses_repository, commit=AsyncMock())
    service = LicenseBackgroundJobsService(uow)

    result = await service.archive_expired_licenses(LicenseArchiverTaskPayload())

    assert result.archived_count == 3
    licenses_repository.archive_expired.assert_awaited_once()
    uow.commit.assert_awaited_once()
