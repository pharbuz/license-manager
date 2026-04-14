from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Path as ApiPath
from fastapi.responses import FileResponse
from kombu.exceptions import OperationalError

from app.license_manager.api.dependencies import get_uow
from app.license_manager.api.v1.schemas.app_packages import (
    AppPackageCreateSchema,
    AppPackageDownloadQuerySchema,
    AppPackageNotifyQuerySchema,
    AppPackageSchema,
    AppPackageUpdateSchema,
)
from app.license_manager.audit import audit_event
from app.license_manager.core.settings import get_settings
from app.license_manager.observability.logging import get_logger
from app.license_manager.services.app_packages_service import AppPackagesService
from app.license_manager.services.email_background_jobs_service import (
    EmailBackgroundJobsService,
)
from app.license_manager.services.errors import EntityNotFoundError
from app.license_manager.services.models.app_packages import (
    AppPackageCreateDto as ServiceAppPackageCreateDto,
)
from app.license_manager.services.models.app_packages import (
    AppPackageUpdateDto as ServiceAppPackageUpdateDto,
)
from app.license_manager.services.models.background_jobs import (
    AppPackageUpdateNotificationTaskPayload,
)
from app.license_manager.tasks.workers.email_background_jobs import (
    enqueue_app_package_update_notification_job,
)
from app.license_manager.uow import UnitOfWork

router = APIRouter(prefix="/app-packages", tags=["AppPackages"])
logger = get_logger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AppPackageSchema)
async def create_app_package(
    payload: AppPackageCreateSchema,
    uow: UnitOfWork = Depends(get_uow),
) -> AppPackageSchema:
    """Create a new app package."""
    service = AppPackagesService(uow)
    result = await service.create_app_package(
        ServiceAppPackageCreateDto.model_validate(payload.model_dump())
    )
    await audit_event(
        uow,
        action="app_packages.create",
        entity_type="app_package",
        entity_id=str(result.id),
        summary=f"Created app package {result.version_number}",
    )
    return AppPackageSchema.model_validate(result.model_dump())


@router.get("", response_model=list[AppPackageSchema])
async def list_app_packages(
    uow: UnitOfWork = Depends(get_uow),
) -> list[AppPackageSchema]:
    """List all app packages."""
    service = AppPackagesService(uow)
    result = await service.list_app_packages()
    return [AppPackageSchema.model_validate(item.model_dump()) for item in result]


@router.get("/{appPackageId}/download")
async def download_app_package(
    app_package_id: UUID = ApiPath(..., alias="appPackageId"),
    query: AppPackageDownloadQuerySchema = Depends(),
) -> FileResponse:
    """Download an app package binary from the configured directory."""
    settings = get_settings()
    root = Path(settings.APP_PACKAGES_DIR)
    candidate = Path(query.file_path)
    resolved = candidate if candidate.is_absolute() else root / candidate
    if not resolved.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    return FileResponse(path=str(resolved), filename=resolved.name)


@router.get("/{appPackageId}/notify", status_code=status.HTTP_204_NO_CONTENT)
async def notify_app_package(
    app_package_id: UUID = ApiPath(..., alias="appPackageId"),
    query: AppPackageNotifyQuerySchema = Depends(),
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    """Record a notification request for an app package version."""
    version_id = query.version_id
    logger.info(
        "Notifying about app package version",
        extra={"app_package_id": str(app_package_id), "version_id": str(version_id)},
    )
    service = AppPackagesService(uow)
    try:
        await service.get_app_package(version_id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    payload = AppPackageUpdateNotificationTaskPayload(version_id=version_id)
    try:
        enqueue_app_package_update_notification_job(payload)
    except OperationalError:
        email_service = EmailBackgroundJobsService(uow)
        await email_service.send_app_package_update_notifications(payload)


@router.get("/{appPackageId}", response_model=AppPackageSchema)
async def get_app_package(
    app_package_id: UUID = ApiPath(..., alias="appPackageId"),
    uow: UnitOfWork = Depends(get_uow),
) -> AppPackageSchema:
    """Get an app package by ID."""
    service = AppPackagesService(uow)
    try:
        result = await service.get_app_package(app_package_id)
        return AppPackageSchema.model_validate(result.model_dump())
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.patch("/{appPackageId}", response_model=AppPackageSchema)
async def update_app_package(
    payload: AppPackageUpdateSchema,
    app_package_id: UUID = ApiPath(..., alias="appPackageId"),
    uow: UnitOfWork = Depends(get_uow),
) -> AppPackageSchema:
    """Update an app package."""
    service = AppPackagesService(uow)
    try:
        result = await service.update_app_package(
            app_package_id,
            ServiceAppPackageUpdateDto.model_validate(payload.model_dump()),
        )
        await audit_event(
            uow,
            action="app_packages.update",
            entity_type="app_package",
            entity_id=str(app_package_id),
            summary=f"Updated app package {result.version_number}",
            metadata={"updated_fields": list(payload.model_dump(exclude_unset=True))},
        )
        return AppPackageSchema.model_validate(result.model_dump())
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/{appPackageId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app_package(
    app_package_id: UUID = ApiPath(..., alias="appPackageId"),
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    """Delete an app package."""
    service = AppPackagesService(uow)
    try:
        await service.delete_app_package(app_package_id)
        await audit_event(
            uow,
            action="app_packages.delete",
            entity_type="app_package",
            entity_id=str(app_package_id),
            summary=f"Deleted app package {app_package_id}",
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{appPackageId}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app_package_via_get(
    app_package_id: UUID = ApiPath(..., alias="appPackageId"),
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    """Delete an app package using a GET endpoint, mirroring the .NET controller action."""
    await delete_app_package(app_package_id, uow)
