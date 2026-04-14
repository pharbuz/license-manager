from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from azure.core.exceptions import ResourceNotFoundError

from app.license_manager.core.helpers import (
    build_contact_person_greeting,
    build_notification_receivers,
)
from app.license_manager.core.settings import get_settings
from app.license_manager.observability.logging import get_logger
from app.license_manager.services.base_service import BaseService
from app.license_manager.services.email_service import EmailService
from app.license_manager.services.models.background_jobs import (
    LicenseArchiverTaskPayload,
    LicenseArchiverTaskResult,
    LicenseCheckTaskPayload,
    LicenseCheckTaskResult,
)
from app.license_manager.services.models.smtp_credentials import (
    SmtpCredentialSecretPayload,
)

logger = get_logger(__name__)


class LicenseBackgroundJobsService(BaseService):
    async def check_license_expirations(
        self,
        payload: LicenseCheckTaskPayload,
    ) -> LicenseCheckTaskResult:
        now = datetime.now(UTC).replace(tzinfo=None)
        days_to_check = self._resolve_days_to_check(payload)
        result = LicenseCheckTaskResult(total_days_processed=len(days_to_check))

        if not days_to_check:
            logger.info("No days configured for license expiration checks")
            return result

        smtp = await self._fetch_smtp_credentials()
        email_service = EmailService(smtp) if smtp else None
        had_updates = False

        for day in days_to_check:
            target_date: date = (now + timedelta(days=day)).date()
            rows = await self.uow.licenses.list_expiring_with_customer_and_product(
                target_date
            )
            result.total_expiring_found += len(rows)

            for license_entity, customer_entity, product_entity in rows:
                if customer_entity is None or not customer_entity.notifications_enabled:
                    result.notifications_skipped += 1
                    continue

                if license_entity.notification_date.date() == now.date():
                    result.notifications_skipped += 1
                    continue

                if email_service is None:
                    result.notifications_failed += 1
                    continue

                receivers = self._build_receivers(
                    license_email=license_entity.license_email,
                    customer_email=customer_entity.email,
                    double_send=license_entity.double_send,
                )

                try:
                    await email_service.send_notification(
                        receivers=receivers,
                        subject=self._build_license_expiration_subject(
                            product_entity.name if product_entity else "license"
                        ),
                        text_body=self._build_license_expiration_text_body(
                            person_name=self._build_person_name(
                                customer_entity.contact_person_name
                            ),
                            customer_name=customer_entity.name,
                            product_name=(
                                product_entity.name if product_entity else "license"
                            ),
                            days_to_expire=day,
                            expiration_date=license_entity.end_date.strftime(
                                "%d.%m.%Y"
                            ),
                            license_key=license_entity.license_key,
                        ),
                        template_name="license_expiration_notification.mjml",
                        context={
                            "person_name": self._build_person_name(
                                customer_entity.contact_person_name
                            ),
                            "customer_name": customer_entity.name,
                            "product_name": (
                                product_entity.name if product_entity else "license"
                            ),
                            "days_to_expire": day,
                            "expiration_date": license_entity.end_date.strftime(
                                "%d.%m.%Y"
                            ),
                            "license_key": license_entity.license_key,
                        },
                    )
                except Exception:
                    result.notifications_failed += 1
                    logger.exception(
                        "Failed to send expiration notification",
                        extra={
                            "license_id": str(license_entity.id),
                            "customer_id": str(customer_entity.id),
                            "days_to_expire": day,
                        },
                    )
                    continue

                license_entity.notification_date = now
                await self.uow.licenses.save(license_entity)
                had_updates = True
                result.notifications_sent += 1

        if had_updates:
            await self.commit()

        logger.info(
            "License expiration checker job completed",
            extra=result.model_dump(),
        )
        return result

    async def archive_expired_licenses(
        self,
        payload: LicenseArchiverTaskPayload,
    ) -> LicenseArchiverTaskResult:
        del payload

        now = datetime.now(UTC).replace(tzinfo=None)
        threshold = now - timedelta(days=1)

        archived_count = await self.uow.licenses.archive_expired(threshold)
        await self.commit()

        result = LicenseArchiverTaskResult(archived_count=archived_count)
        logger.info("License archiver job completed", extra=result.model_dump())
        return result

    async def _fetch_smtp_credentials(self) -> SmtpCredentialSecretPayload | None:
        try:
            _, _, payload = await self.uow.smtp_credentials.fetch()
        except ResourceNotFoundError:
            logger.warning(
                "SMTP credentials were not found. Notifications cannot be sent."
            )
            return None
        return payload

    def _resolve_days_to_check(self, payload: LicenseCheckTaskPayload) -> list[int]:
        if payload.days_from_today_to_check is not None:
            return [day for day in payload.days_from_today_to_check if day > 0]

        settings = get_settings()
        if isinstance(settings.LICENSE_CHECK_DAYS_FROM_TODAY_TO_CHECK, list):
            return [
                day
                for day in settings.LICENSE_CHECK_DAYS_FROM_TODAY_TO_CHECK
                if day > 0
            ]
        return []

    @staticmethod
    def _build_person_name(contact_person_name: str | None) -> str:
        return build_contact_person_greeting(contact_person_name)

    @staticmethod
    def _build_receivers(
        *,
        license_email: str,
        customer_email: str | None,
        double_send: bool,
    ) -> list[str]:
        return build_notification_receivers(
            license_email=license_email,
            customer_email=customer_email,
            double_send=double_send,
        )

    @staticmethod
    def _build_license_expiration_subject(product_name: str) -> str:
        if product_name == "AppPackage":
            return "Application Package license"
        return f"{product_name} license"

    @staticmethod
    def _build_license_expiration_text_body(
        *,
        person_name: str,
        customer_name: str,
        product_name: str,
        days_to_expire: int,
        expiration_date: str,
        license_key: str,
    ) -> str:
        return "\n".join(
            [
                person_name,
                "",
                (
                    f"We would like to kindly inform that your {product_name} "
                    f"license is about to expire. The license will expire in "
                    f"{days_to_expire} days."
                ),
                "",
                f"Customer: {customer_name}",
                f"Expiration date: {expiration_date}",
                f"License key: {license_key}",
            ]
        )
