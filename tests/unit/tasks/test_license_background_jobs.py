from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.license_manager.services.models.background_jobs import (
    LicenseArchiverTaskPayload,
    LicenseArchiverTaskResult,
    LicenseCheckTaskPayload,
    LicenseCheckTaskResult,
)
from app.license_manager.tasks import celery_app
from app.license_manager.tasks.workers import license_background_jobs


class _UowContext:
    async def __aenter__(self):
        return object()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


def test_parse_cron_expression_valid() -> None:
    schedule = celery_app._parse_cron_expression("*/5 * * * *")
    assert schedule is not None


def test_parse_cron_expression_invalid() -> None:
    with pytest.raises(ValueError):
        celery_app._parse_cron_expression("*/5 * *")


def test_configure_beat_schedule() -> None:
    app = celery_app.Celery("test")
    app.conf.beat_schedule = {}
    app.conf.task_queues = ()
    app.conf.task_routes = []
    settings = type(
        "SettingsStub",
        (),
        {
            "LICENSE_CHECK_CRON": "*/10 * * * *",
            "LICENSE_ARCHIVER_CRON": "0 1 * * *",
            "CELERY_TASK_DEFAULT_QUEUE": "license_manager",
        },
    )()

    celery_app.configure_beat_schedule(app, settings)

    assert "license-checker" in app.conf.beat_schedule
    assert "license-archiver" in app.conf.beat_schedule


def test_check_license_expirations_task(monkeypatch) -> None:
    expected = LicenseCheckTaskResult(
        total_days_processed=1,
        total_expiring_found=3,
        notifications_sent=2,
        notifications_skipped=1,
        notifications_failed=0,
    )

    async def _fake_runner(_payload: LicenseCheckTaskPayload) -> LicenseCheckTaskResult:
        return expected

    monkeypatch.setattr(license_background_jobs, "run_license_checker", _fake_runner)

    result = license_background_jobs.check_license_expirations.run(
        payload=LicenseCheckTaskPayload(days_from_today_to_check=[7])
    )

    assert result == expected.model_dump()


def test_archive_expired_licenses_task(monkeypatch) -> None:
    expected = LicenseArchiverTaskResult(archived_count=5)

    async def _fake_runner(
        _payload: LicenseArchiverTaskPayload,
    ) -> LicenseArchiverTaskResult:
        return expected

    monkeypatch.setattr(license_background_jobs, "run_license_archiver", _fake_runner)

    result = license_background_jobs.archive_expired_licenses.run(
        payload=LicenseArchiverTaskPayload(run_reason="test")
    )

    assert result == expected.model_dump()


@pytest.mark.asyncio
async def test_run_license_checker_delegates_to_service(monkeypatch) -> None:
    expected = LicenseCheckTaskResult(total_days_processed=1)
    service = AsyncMock()
    service.check_license_expirations.return_value = expected

    monkeypatch.setattr(license_background_jobs, "new_uow", lambda: _UowContext())
    monkeypatch.setattr(
        license_background_jobs,
        "LicenseBackgroundJobsService",
        lambda _uow: service,
    )

    result = await license_background_jobs.run_license_checker(
        LicenseCheckTaskPayload()
    )

    assert result == expected


@pytest.mark.asyncio
async def test_run_license_archiver_delegates_to_service(monkeypatch) -> None:
    expected = LicenseArchiverTaskResult(archived_count=3)
    service = AsyncMock()
    service.archive_expired_licenses.return_value = expected

    monkeypatch.setattr(license_background_jobs, "new_uow", lambda: _UowContext())
    monkeypatch.setattr(
        license_background_jobs,
        "LicenseBackgroundJobsService",
        lambda _uow: service,
    )

    result = await license_background_jobs.run_license_archiver(
        LicenseArchiverTaskPayload()
    )

    assert result == expected
