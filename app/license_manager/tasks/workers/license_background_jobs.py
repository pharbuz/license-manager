from __future__ import annotations

import asyncio

from celery import shared_task

from app.license_manager.services.license_background_jobs_service import (
    LicenseBackgroundJobsService,
)
from app.license_manager.services.models.background_jobs import (
    LicenseArchiverTaskPayload,
    LicenseArchiverTaskResult,
    LicenseCheckTaskPayload,
    LicenseCheckTaskResult,
)
from app.license_manager.tasks.workers.helpers import new_uow


async def run_license_checker(
    payload: LicenseCheckTaskPayload,
) -> LicenseCheckTaskResult:
    async with new_uow() as uow:
        service = LicenseBackgroundJobsService(uow)
        return await service.check_license_expirations(payload)


async def run_license_archiver(
    payload: LicenseArchiverTaskPayload,
) -> LicenseArchiverTaskResult:
    async with new_uow() as uow:
        service = LicenseBackgroundJobsService(uow)
        return await service.archive_expired_licenses(payload)


@shared_task(
    bind=True,
    name=(
        "app.license_manager.tasks.workers.license_background_jobs."
        "check_license_expirations"
    ),
    pydantic=True,
)
def check_license_expirations(
    self,
    payload: LicenseCheckTaskPayload | None = None,
) -> LicenseCheckTaskResult:
    effective_payload = payload or LicenseCheckTaskPayload()
    return asyncio.run(run_license_checker(effective_payload))


@shared_task(
    bind=True,
    name=(
        "app.license_manager.tasks.workers.license_background_jobs."
        "archive_expired_licenses"
    ),
    pydantic=True,
)
def archive_expired_licenses(
    self,
    payload: LicenseArchiverTaskPayload | None = None,
) -> LicenseArchiverTaskResult:
    effective_payload = payload or LicenseArchiverTaskPayload()
    return asyncio.run(run_license_archiver(effective_payload))
