from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.license_manager.db.models import AppPackage, Customer, License, Product
from app.license_manager.services.email_background_jobs_service import (
    EmailBackgroundJobsService,
)
from app.license_manager.services.models.background_jobs import (
    AppPackageUpdateNotificationTaskPayload,
    InitialLicenseNotificationTaskPayload,
)
from app.license_manager.services.models.email_notifications import EmailAttachment
from app.license_manager.services.models.smtp_credentials import (
    SmtpCredentialSecretPayload,
)


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
async def test_send_initial_license_notification_sends_email(
    monkeypatch: pytest.MonkeyPatch,
    smtp_payload: SmtpCredentialSecretPayload,
) -> None:
    license_id = uuid4()
    uow = SimpleNamespace(
        licenses=SimpleNamespace(
            get_with_customer_and_product=AsyncMock(
                return_value=(
                    License(
                        id=license_id,
                        customer_id=uuid4(),
                        product_id=uuid4(),
                        kind_id=None,
                        license_count=1,
                        license_state="Active",
                        license_key="LIC-123",
                        license_email="owner@example.com",
                        double_send=True,
                        begin_date=datetime(2026, 1, 1),
                        end_date=datetime(2026, 12, 31),
                        notification_date=datetime(1970, 1, 1),
                    ),
                    Customer(
                        id=uuid4(),
                        name="Acme",
                        contact_person_name="John Doe",
                        email="customer@example.com",
                        notifications_enabled=True,
                        gem_fury_used=True,
                        customer_symbol="ACM",
                    ),
                    Product(
                        id=uuid4(),
                        name="AppPackage",
                        kind="Agent",
                    ),
                )
            )
        ),
        app_packages=SimpleNamespace(get_max_version=AsyncMock(return_value="1.2.3")),
    )
    service = EmailBackgroundJobsService(uow)

    monkeypatch.setattr(
        service, "_fetch_smtp_credentials", AsyncMock(return_value=smtp_payload)
    )

    send_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "app.license_manager.services.email_service.EmailService.send_notification",
        send_mock,
    )

    result = await service.send_initial_license_notification(
        InitialLicenseNotificationTaskPayload(license_id=license_id)
    )

    assert result.sent is True
    send_mock.assert_awaited_once()
    assert send_mock.await_args.kwargs["template_name"] == "initial_notification.mjml"
    assert send_mock.await_args.kwargs["receivers"] == [
        "owner@example.com",
        "customer@example.com",
    ]


@pytest.mark.asyncio
async def test_send_app_package_update_notifications_sends_all_targets(
    monkeypatch: pytest.MonkeyPatch,
    smtp_payload: SmtpCredentialSecretPayload,
) -> None:
    version_id = uuid4()
    uow = SimpleNamespace(
        licenses=SimpleNamespace(
            list_active_app_package_notification_targets=AsyncMock(
                return_value=[
                    (
                        License(
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
                            end_date=datetime(2026, 12, 31),
                            notification_date=datetime(1970, 1, 1),
                        ),
                        Customer(
                            id=uuid4(),
                            name="Acme",
                            email="customer@example.com",
                            notifications_enabled=True,
                            gem_fury_used=True,
                            customer_symbol="ACM",
                        ),
                    )
                ]
            )
        ),
        app_packages=SimpleNamespace(
            get_by_id=AsyncMock(
                return_value=AppPackage(
                    id=version_id,
                    version_number="1.2.3",
                    binary_name="agent.bin",
                    gem_fury_url="https://gem.fury.io/example",
                    binary_url="https://downloads.example.com/agent.bin",
                )
            )
        ),
    )
    service = EmailBackgroundJobsService(uow)

    monkeypatch.setattr(
        service, "_fetch_smtp_credentials", AsyncMock(return_value=smtp_payload)
    )
    monkeypatch.setattr(
        service,
        "_load_app_package_attachment",
        lambda _binary_name: EmailAttachment(
            filename="agent.bin",
            content=b"payload",
            mime_type="application/octet-stream",
        ),
    )

    send_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "app.license_manager.services.email_service.EmailService.send_notification",
        send_mock,
    )

    result = await service.send_app_package_update_notifications(
        AppPackageUpdateNotificationTaskPayload(version_id=version_id)
    )

    assert result.total_targets == 1
    assert result.notifications_sent == 1
    assert result.notifications_failed == 0
    send_mock.assert_awaited_once()
    assert send_mock.await_args.kwargs["template_name"] == "update_notification.mjml"
