from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.license_manager.services.email_service import EmailService
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
async def test_send_notification_with_template(monkeypatch, smtp_payload) -> None:
    service = EmailService(smtp_payload)

    monkeypatch.setattr(
        "app.license_manager.services.email_service.mjml2html",
        lambda _markup: {"html": "<html><body>ok</body></html>", "errors": []},
    )

    send_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "app.license_manager.services.email_service.aiosmtplib.send", send_mock
    )

    await service.send_notification(
        receivers=["to@example.com"],
        subject="Subject",
        text_body="Text body",
        template_name="license_expiration_notification.mjml",
        context={
            "person_name": "Dear John",
            "customer_name": "Acme",
            "product_name": "AppPackage",
            "days_to_expire": 7,
            "expiration_date": "20.04.2026",
            "license_key": "abc",
        },
    )

    send_mock.assert_awaited_once()
    message = send_mock.await_args.args[0]
    assert message["To"] == "to@example.com"
    assert message.get_body(("html",)) is not None


@pytest.mark.asyncio
async def test_send_notification_requires_receivers(smtp_payload) -> None:
    service = EmailService(smtp_payload)

    with pytest.raises(ValueError):
        await service.send_notification(
            receivers=[],
            subject="Subject",
            text_body="Text body",
        )


@pytest.mark.asyncio
async def test_send_notification_supports_cc_and_attachments(
    monkeypatch, smtp_payload
) -> None:
    service = EmailService(smtp_payload)
    send_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "app.license_manager.services.email_service.aiosmtplib.send", send_mock
    )

    await service.send_notification(
        receivers=["to@example.com"],
        cc=["cc@example.com"],
        subject="Subject",
        text_body="Text body",
        attachments=[
            EmailAttachment(
                filename="agent.bin",
                content=b"payload",
                mime_type="application/octet-stream",
            )
        ],
    )

    send_mock.assert_awaited_once()
    message = send_mock.await_args.args[0]
    assert message["Cc"] == "cc@example.com"
    assert any(
        part.get_filename() == "agent.bin" for part in message.iter_attachments()
    )


@pytest.mark.parametrize(
    ("template_name", "context"),
    [
        (
            "license_expiration_notification.mjml",
            {
                "person_name": "Dear John",
                "customer_name": "Acme",
                "product_name": "AppPackage",
                "days_to_expire": 7,
                "expiration_date": "20.04.2026",
                "license_key": "LIC-123",
            },
        ),
        (
            "initial_notification.mjml",
            {
                "license_key": "LIC-123",
                "app_package_max_version": "1.2.3",
                "days_to_expire": 90,
                "expiration_date": "20.04.2026",
            },
        ),
        (
            "update_notification.mjml",
            {
                "version_number": "1.2.3",
                "gem_fury": "https://gem.fury.io/example",
                "license_key": "LIC-123",
            },
        ),
    ],
)
def test_render_all_mail_templates(
    monkeypatch,
    smtp_payload,
    template_name: str,
    context: dict[str, object],
) -> None:
    service = EmailService(smtp_payload)
    monkeypatch.setattr(
        "app.license_manager.services.email_service.mjml2html",
        lambda markup: {"html": markup, "errors": []},
    )

    rendered = service._render_mjml_template(template_name, context)

    assert "Support Team" in rendered
