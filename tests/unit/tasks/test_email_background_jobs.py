from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.license_manager.services.models.background_jobs import (
    AppPackageUpdateNotificationTaskPayload,
    AppPackageUpdateNotificationTaskResult,
    InitialLicenseNotificationTaskPayload,
    InitialLicenseNotificationTaskResult,
)
from app.license_manager.tasks.workers import email_background_jobs


class _UowContext:
    async def __aenter__(self):
        return object()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


def test_send_initial_license_notification_task(monkeypatch) -> None:
    expected = InitialLicenseNotificationTaskResult(sent=True)

    async def _fake_runner(
        _payload: InitialLicenseNotificationTaskPayload,
    ) -> InitialLicenseNotificationTaskResult:
        return expected

    monkeypatch.setattr(
        email_background_jobs, "run_initial_license_notification", _fake_runner
    )

    result = email_background_jobs.send_initial_license_notification.run(
        payload=InitialLicenseNotificationTaskPayload(license_id=uuid4())
    )

    assert result == expected.model_dump()


def test_send_app_package_update_notifications_task(monkeypatch) -> None:
    expected = AppPackageUpdateNotificationTaskResult(
        total_targets=2,
        notifications_sent=2,
    )

    async def _fake_runner(
        _payload: AppPackageUpdateNotificationTaskPayload,
    ) -> AppPackageUpdateNotificationTaskResult:
        return expected

    monkeypatch.setattr(
        email_background_jobs, "run_app_package_update_notifications", _fake_runner
    )

    result = email_background_jobs.send_app_package_update_notifications.run(
        payload=AppPackageUpdateNotificationTaskPayload(version_id=uuid4())
    )

    assert result == expected.model_dump()


@pytest.mark.asyncio
async def test_run_initial_license_notification_delegates_to_service(
    monkeypatch,
) -> None:
    expected = InitialLicenseNotificationTaskResult(sent=True)
    service = AsyncMock()
    service.send_initial_license_notification.return_value = expected

    monkeypatch.setattr(email_background_jobs, "new_uow", lambda: _UowContext())
    monkeypatch.setattr(
        email_background_jobs,
        "EmailBackgroundJobsService",
        lambda _uow: service,
    )

    result = await email_background_jobs.run_initial_license_notification(
        InitialLicenseNotificationTaskPayload(license_id=uuid4())
    )

    assert result == expected


@pytest.mark.asyncio
async def test_run_app_package_update_notifications_delegates_to_service(
    monkeypatch,
) -> None:
    expected = AppPackageUpdateNotificationTaskResult(total_targets=1)
    service = AsyncMock()
    service.send_app_package_update_notifications.return_value = expected

    monkeypatch.setattr(email_background_jobs, "new_uow", lambda: _UowContext())
    monkeypatch.setattr(
        email_background_jobs,
        "EmailBackgroundJobsService",
        lambda _uow: service,
    )

    result = await email_background_jobs.run_app_package_update_notifications(
        AppPackageUpdateNotificationTaskPayload(version_id=uuid4())
    )

    assert result == expected
