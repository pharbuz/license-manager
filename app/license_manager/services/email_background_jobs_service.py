from __future__ import annotations

import mimetypes
from datetime import UTC, datetime
from pathlib import Path

from azure.core.exceptions import ResourceNotFoundError

from app.license_manager.core.helpers import build_notification_receivers
from app.license_manager.core.settings import get_settings
from app.license_manager.observability.logging import get_logger
from app.license_manager.services.base_service import BaseService
from app.license_manager.services.email_service import EmailService
from app.license_manager.services.models.background_jobs import (
    AppPackageUpdateNotificationTaskPayload,
    AppPackageUpdateNotificationTaskResult,
    InitialLicenseNotificationTaskPayload,
    InitialLicenseNotificationTaskResult,
)
from app.license_manager.services.models.email_notifications import EmailAttachment
from app.license_manager.services.models.smtp_credentials import (
    SmtpCredentialSecretPayload,
)

logger = get_logger(__name__)


class EmailBackgroundJobsService(BaseService):
    async def send_initial_license_notification(
        self,
        payload: InitialLicenseNotificationTaskPayload,
    ) -> InitialLicenseNotificationTaskResult:
        smtp = await self._fetch_smtp_credentials()
        if smtp is None:
            return InitialLicenseNotificationTaskResult(
                skipped_reason="smtp_credentials_missing"
            )

        row = await self.uow.licenses.get_with_customer_and_product(payload.license_id)
        if row is None:
            return InitialLicenseNotificationTaskResult(
                skipped_reason="license_not_found"
            )

        license_entity, customer_entity, product_entity = row
        if customer_entity is None or product_entity is None:
            return InitialLicenseNotificationTaskResult(
                skipped_reason="license_dependencies_missing"
            )
        if not customer_entity.notifications_enabled:
            return InitialLicenseNotificationTaskResult(
                skipped_reason="notifications_disabled"
            )
        if product_entity.name.lower() != "apppackage":
            return InitialLicenseNotificationTaskResult(
                skipped_reason="unsupported_product"
            )

        app_package_max_version = await self.uow.app_packages.get_max_version()

        receivers = build_notification_receivers(
            license_email=license_entity.license_email,
            customer_email=customer_entity.email,
            double_send=license_entity.double_send,
        )
        days_to_expire = (
            license_entity.end_date.date()
            - datetime.now(UTC).replace(tzinfo=None).date()
        ).days

        email_service = EmailService(smtp)
        try:
            await email_service.send_notification(
                receivers=receivers,
                subject="Your Application Package license is active",
                text_body=self._build_initial_notification_text_body(
                    license_key=license_entity.license_key,
                    app_package_max_version=app_package_max_version,
                    days_to_expire=days_to_expire,
                    expiration_date=license_entity.end_date.strftime("%d.%m.%Y"),
                ),
                template_name="initial_notification.mjml",
                context={
                    "license_key": license_entity.license_key,
                    "app_package_max_version": app_package_max_version,
                    "days_to_expire": days_to_expire,
                    "expiration_date": license_entity.end_date.strftime("%d.%m.%Y"),
                },
            )
        except Exception:
            logger.exception(
                "Failed to send initial license notification",
                extra={"license_id": str(payload.license_id)},
            )
            return InitialLicenseNotificationTaskResult(skipped_reason="send_failed")

        return InitialLicenseNotificationTaskResult(sent=True)

    async def send_app_package_update_notifications(
        self,
        payload: AppPackageUpdateNotificationTaskPayload,
    ) -> AppPackageUpdateNotificationTaskResult:
        smtp = await self._fetch_smtp_credentials()
        if smtp is None:
            return AppPackageUpdateNotificationTaskResult(
                skipped_reason="smtp_credentials_missing"
            )

        app_package = await self.uow.app_packages.get_by_id(payload.version_id)
        if app_package is None:
            return AppPackageUpdateNotificationTaskResult(
                skipped_reason="app_package_not_found"
            )

        rows = await self.uow.licenses.list_active_app_package_notification_targets()

        attachment = self._load_app_package_attachment(app_package.binary_name)
        if attachment is None:
            return AppPackageUpdateNotificationTaskResult(
                total_targets=len(rows),
                skipped_reason="binary_attachment_missing",
            )

        result = AppPackageUpdateNotificationTaskResult(total_targets=len(rows))
        email_service = EmailService(smtp)

        for license_entity, customer_entity in rows:
            receivers = build_notification_receivers(
                license_email=license_entity.license_email,
                customer_email=customer_entity.email,
                double_send=license_entity.double_send,
            )

            try:
                await email_service.send_notification(
                    receivers=receivers,
                    subject="New version of Application Package is available",
                    text_body=self._build_app_package_update_text_body(
                        version_number=app_package.version_number,
                        gem_fury=app_package.gem_fury_url,
                        license_key=license_entity.license_key,
                    ),
                    attachments=[attachment],
                    template_name="update_notification.mjml",
                    context={
                        "version_number": app_package.version_number,
                        "gem_fury": app_package.gem_fury_url,
                        "license_key": license_entity.license_key,
                    },
                )
            except Exception:
                result.notifications_failed += 1
                logger.exception(
                    "Failed to send app package update notification",
                    extra={
                        "version_id": str(payload.version_id),
                        "license_id": str(license_entity.id),
                        "customer_id": str(customer_entity.id),
                    },
                )
                continue

            result.notifications_sent += 1

        return result

    async def _fetch_smtp_credentials(self) -> SmtpCredentialSecretPayload | None:
        if self.uow.smtp_credentials is None:
            logger.warning(
                "SMTP credentials repository is not initialized on UnitOfWork. "
                "Notifications cannot be sent."
            )
            return None

        try:
            _, _, payload = await self.uow.smtp_credentials.fetch()
        except ResourceNotFoundError:
            logger.warning(
                "SMTP credentials were not found. Notifications cannot be sent."
            )
            return None
        return payload

    @staticmethod
    def _load_app_package_attachment(binary_name: str) -> EmailAttachment | None:
        settings = get_settings()
        attachment_path = Path(settings.APP_PACKAGES_DIR) / binary_name
        if not attachment_path.exists():
            logger.warning(
                "App package binary attachment was not found",
                extra={"attachment_path": str(attachment_path)},
            )
            return None

        mime_type = mimetypes.guess_type(attachment_path.name)[0]
        return EmailAttachment(
            filename=attachment_path.name,
            content=attachment_path.read_bytes(),
            mime_type=mime_type or "application/octet-stream",
        )

    @staticmethod
    def _build_initial_notification_text_body(
        *,
        license_key: str,
        app_package_max_version: str,
        days_to_expire: int,
        expiration_date: str,
    ) -> str:
        return "\n".join(
            [
                "Hi there,",
                "",
                "We would like to kindly inform that your Application Package "
                "license is active.",
                f"License key: {license_key}",
                f"App package max version: {app_package_max_version}",
                f"The license will expire in {days_to_expire} days.",
                f"Expiration date: {expiration_date}",
            ]
        )

    @staticmethod
    def _build_app_package_update_text_body(
        *,
        version_number: str,
        gem_fury: str,
        license_key: str,
    ) -> str:
        return "\n".join(
            [
                "Hi there,",
                "",
                "We would like to kindly inform you that our Application Package "
                "has a new version available.",
                f"Latest version: {version_number}",
                f"Package repository: {gem_fury}",
                f"License key: {license_key}",
            ]
        )
