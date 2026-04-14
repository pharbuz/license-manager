from __future__ import annotations

import html
import mimetypes
import re
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import aiosmtplib
from mjml import mjml2html

from app.license_manager.observability.logging import get_logger
from app.license_manager.services.models.email_notifications import EmailAttachment
from app.license_manager.services.models.smtp_credentials import (
    SmtpCredentialSecretPayload,
)

logger = get_logger(__name__)


class EmailService:
    _TEMPLATE_DIR = (
        Path(__file__).resolve().parent.parent / "templates" / "email" / "mjml"
    )

    def __init__(self, smtp_config: SmtpCredentialSecretPayload) -> None:
        self._smtp_config = smtp_config

    async def send_notification(
        self,
        *,
        receivers: list[str],
        subject: str,
        text_body: str,
        cc: list[str] | None = None,
        attachments: list[EmailAttachment] | None = None,
        template_name: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        if not receivers:
            raise ValueError("At least one recipient address is required")

        html_body: str | None = None
        if template_name:
            html_body = self._render_mjml_template(template_name, context or {})

        cc_receivers = cc or []
        message = self._build_message(
            receivers,
            subject,
            text_body,
            html_body,
            cc_receivers,
            attachments or [],
        )

        sender = self._smtp_config.sender_email or self._smtp_config.username
        await aiosmtplib.send(
            message,
            hostname=self._smtp_config.host,
            port=self._smtp_config.port,
            start_tls=self._smtp_config.use_tls,
            use_tls=self._smtp_config.use_ssl,
            username=self._smtp_config.username,
            password=self._smtp_config.password,
            sender=sender,
            recipients=[*receivers, *cc_receivers],
            validate_certs=False,
        )

        logger.info(
            "Notification email sent",
            extra={
                "recipients": receivers,
                "subject": subject,
            },
        )

    def _render_mjml_template(self, template_name: str, context: dict[str, Any]) -> str:
        template_path = self._TEMPLATE_DIR / template_name
        template = template_path.read_text(encoding="utf-8")
        mjml_markup = self._interpolate_template(template, context)
        result = mjml2html(mjml_markup)

        if isinstance(result, dict):
            html_body = result.get("html")
            errors = result.get("errors") or []
            if errors:
                logger.warning(
                    "MJML template rendered with errors",
                    extra={"template": template_name, "errors": errors},
                )
            if html_body:
                return html_body
            raise ValueError(f"MJML rendering failed for {template_name}")

        if isinstance(result, str):
            return result

        html_body = getattr(result, "html", None)
        if html_body:
            return html_body
        raise ValueError(f"Unsupported MJML response for {template_name}")

    @staticmethod
    def _interpolate_template(template: str, context: dict[str, Any]) -> str:
        raw_pattern = re.compile(r"{{{\s*([a-zA-Z0-9_]+)\s*}}}")
        pattern = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")

        def replace_raw(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in context:
                return match.group(0)
            value = context[key]
            return "" if value is None else str(value)

        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in context:
                return match.group(0)
            value = context[key]
            return html.escape("" if value is None else str(value))

        return pattern.sub(replace, raw_pattern.sub(replace_raw, template))

    def _build_message(
        self,
        receivers: list[str],
        subject: str,
        text_body: str,
        html_body: str | None,
        cc_receivers: list[str],
        attachments: list[EmailAttachment],
    ) -> EmailMessage:
        sender = self._smtp_config.sender_email or self._smtp_config.username
        message = EmailMessage()
        message["From"] = sender
        message["To"] = ", ".join(receivers)
        if cc_receivers:
            message["Cc"] = ", ".join(cc_receivers)
        message["Subject"] = subject
        message.set_content(text_body)
        if html_body:
            message.add_alternative(html_body, subtype="html")
        for attachment in attachments:
            maintype, subtype = self._resolve_mime_type(attachment.mime_type)
            message.add_attachment(
                attachment.content,
                maintype=maintype,
                subtype=subtype,
                filename=attachment.filename,
            )
        return message

    @staticmethod
    def _resolve_mime_type(mime_type: str) -> tuple[str, str]:
        if "/" in mime_type:
            maintype, subtype = mime_type.split("/", maxsplit=1)
            return maintype, subtype

        guessed_mime_type, _ = mimetypes.guess_type(f"attachment.{mime_type}")
        if guessed_mime_type and "/" in guessed_mime_type:
            maintype, subtype = guessed_mime_type.split("/", maxsplit=1)
            return maintype, subtype
        return "application", "octet-stream"
