from __future__ import annotations

from uuid import UUID

from app.license_manager.services.models.common import BaseCamelModel


class LicenseCheckTaskPayload(BaseCamelModel):
    days_from_today_to_check: list[int] | None = None


class LicenseCheckTaskResult(BaseCamelModel):
    total_days_processed: int = 0
    total_expiring_found: int = 0
    notifications_sent: int = 0
    notifications_skipped: int = 0
    notifications_failed: int = 0


class LicenseArchiverTaskPayload(BaseCamelModel):
    run_reason: str | None = None


class LicenseArchiverTaskResult(BaseCamelModel):
    archived_count: int = 0


class InitialLicenseNotificationTaskPayload(BaseCamelModel):
    license_id: UUID


class InitialLicenseNotificationTaskResult(BaseCamelModel):
    sent: bool = False
    skipped_reason: str | None = None


class AppPackageUpdateNotificationTaskPayload(BaseCamelModel):
    version_id: UUID


class AppPackageUpdateNotificationTaskResult(BaseCamelModel):
    total_targets: int = 0
    notifications_sent: int = 0
    notifications_failed: int = 0
    skipped_reason: str | None = None
