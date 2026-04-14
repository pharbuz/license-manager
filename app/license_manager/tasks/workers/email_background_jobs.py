from __future__ import annotations

import asyncio

from celery import shared_task

from app.license_manager.services.email_background_jobs_service import (
    EmailBackgroundJobsService,
)
from app.license_manager.services.models.background_jobs import (
    AppPackageUpdateNotificationTaskPayload,
    AppPackageUpdateNotificationTaskResult,
    InitialLicenseNotificationTaskPayload,
    InitialLicenseNotificationTaskResult,
)
from app.license_manager.tasks.workers.helpers import new_uow


async def run_initial_license_notification(
    payload: InitialLicenseNotificationTaskPayload,
) -> InitialLicenseNotificationTaskResult:
    async with new_uow() as uow:
        service = EmailBackgroundJobsService(uow)
        return await service.send_initial_license_notification(payload)


async def run_app_package_update_notifications(
    payload: AppPackageUpdateNotificationTaskPayload,
) -> AppPackageUpdateNotificationTaskResult:
    async with new_uow() as uow:
        service = EmailBackgroundJobsService(uow)
        return await service.send_app_package_update_notifications(payload)


def enqueue_initial_license_notification_job(
    payload: InitialLicenseNotificationTaskPayload,
) -> None:
    send_initial_license_notification.apply_async(
        kwargs={"payload": payload.model_dump(mode="json")}
    )


def enqueue_app_package_update_notification_job(
    payload: AppPackageUpdateNotificationTaskPayload,
) -> None:
    send_app_package_update_notifications.apply_async(
        kwargs={"payload": payload.model_dump(mode="json")}
    )


@shared_task(
    bind=True,
    name=(
        "app.license_manager.tasks.workers.email_background_jobs."
        "send_initial_license_notification"
    ),
    pydantic=True,
)
def send_initial_license_notification(
    self,
    payload: InitialLicenseNotificationTaskPayload,
) -> InitialLicenseNotificationTaskResult:
    return asyncio.run(run_initial_license_notification(payload))


@shared_task(
    bind=True,
    name=(
        "app.license_manager.tasks.workers.email_background_jobs."
        "send_app_package_update_notifications"
    ),
    pydantic=True,
)
def send_app_package_update_notifications(
    self,
    payload: AppPackageUpdateNotificationTaskPayload,
) -> AppPackageUpdateNotificationTaskResult:
    return asyncio.run(run_app_package_update_notifications(payload))
