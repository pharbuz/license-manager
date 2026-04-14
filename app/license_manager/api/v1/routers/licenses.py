from __future__ import annotations

import base64
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.license_manager.api.dependencies import get_uow
from app.license_manager.api.v1.schemas.licenses import (
    LicenseCreateSchema,
    LicenseGeneratedKeySchema,
    LicenseGenerateQuerySchema,
    LicenseSchema,
    LicenseUpdateSchema,
)
from app.license_manager.audit import audit_event
from app.license_manager.services.errors import EntityNotFoundError
from app.license_manager.services.licenses_service import LicensesService
from app.license_manager.services.models.licenses import (
    LicenseCreateDto as ServiceLicenseCreateDto,
)
from app.license_manager.services.models.licenses import (
    LicenseUpdateDto as ServiceLicenseUpdateDto,
)
from app.license_manager.uow import UnitOfWork

router = APIRouter(prefix="/licenses", tags=["Licenses"])

_LICENSE_HASH = [
    0,
    21,
    22,
    13,
    3,
    23,
    11,
    20,
    14,
    4,
    8,
    1,
    15,
    18,
    5,
    10,
    9,
    7,
    16,
    17,
    2,
    6,
    19,
    12,
]


def _generate_license_key(
    customer_symbol: str, end_date: datetime, license_count: int
) -> str:
    if license_count <= 99:
        count = f"00{license_count}"
    elif license_count <= 999:
        count = f"0{license_count}"
    else:
        count = str(license_count)

    license_code = f"{customer_symbol}/{count}/{end_date:%d%m%Y}"
    encoded_key = base64.b64encode(license_code.encode("utf-8")).decode("utf-8")
    return "".join(encoded_key[index] for index in _LICENSE_HASH)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=LicenseSchema)
async def create_license(
    payload: LicenseCreateSchema,
    uow: UnitOfWork = Depends(get_uow),
) -> LicenseSchema:
    """Create a new license."""
    service = LicensesService(uow)
    result = await service.create_license(
        ServiceLicenseCreateDto.model_validate(payload.model_dump())
    )
    await audit_event(
        uow,
        action="licenses.create",
        entity_type="license",
        entity_id=str(result.id),
        summary=f"Created license {result.license_key}",
        metadata={
            "customer_id": str(result.customer_id) if result.customer_id else None
        },
    )
    return LicenseSchema.model_validate(result.model_dump())


@router.get("", response_model=list[LicenseSchema])
async def list_licenses(
    uow: UnitOfWork = Depends(get_uow),
) -> list[LicenseSchema]:
    """List all licenses."""
    service = LicensesService(uow)
    result = await service.list_licenses()
    return [LicenseSchema.model_validate(item.model_dump()) for item in result]


@router.get("/archive", response_model=list[LicenseSchema])
async def list_archive_licenses(
    uow: UnitOfWork = Depends(get_uow),
) -> list[LicenseSchema]:
    """List archived licenses."""
    service = LicensesService(uow)
    result = await service.list_licenses()
    archived = [item for item in result if item.license_state.lower() == "archived"]
    return [LicenseSchema.model_validate(item.model_dump()) for item in archived]


@router.post("/generate", response_model=LicenseGeneratedKeySchema)
async def generate_license(
    payload: LicenseGenerateQuerySchema,
) -> LicenseGeneratedKeySchema:
    """Generate a license key."""
    return LicenseGeneratedKeySchema(
        license_key=_generate_license_key(
            payload.customer_symbol,
            payload.end_date,
            payload.license_count,
        )
    )


@router.get("/customer/{customerId}", response_model=list[LicenseSchema])
async def list_licenses_by_customer(
    customer_id: UUID = Path(..., alias="customerId"),
    uow: UnitOfWork = Depends(get_uow),
) -> list[LicenseSchema]:
    """List all licenses for a specific customer."""
    service = LicensesService(uow)
    result = await service.list_licenses_by_customer(customer_id)
    return [LicenseSchema.model_validate(item.model_dump()) for item in result]


@router.get("/{licenseId}/archive", response_model=LicenseSchema)
async def archive_license(
    license_id: UUID = Path(..., alias="licenseId"),
    uow: UnitOfWork = Depends(get_uow),
) -> LicenseSchema:
    """Archive a license."""
    service = LicensesService(uow)
    try:
        result = await service.update_license(
            license_id,
            ServiceLicenseUpdateDto(license_state="Archived"),
        )
        return LicenseSchema.model_validate(result.model_dump())
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{licenseId}/unarchive", response_model=LicenseSchema)
async def unarchive_license(
    license_id: UUID = Path(..., alias="licenseId"),
    uow: UnitOfWork = Depends(get_uow),
) -> LicenseSchema:
    """Unarchive a license."""
    service = LicensesService(uow)
    try:
        result = await service.update_license(
            license_id,
            ServiceLicenseUpdateDto(license_state="Active"),
        )
        return LicenseSchema.model_validate(result.model_dump())
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{licenseId}", response_model=LicenseSchema)
async def get_license(
    license_id: UUID = Path(..., alias="licenseId"),
    uow: UnitOfWork = Depends(get_uow),
) -> LicenseSchema:
    """Get a license by ID."""
    service = LicensesService(uow)
    try:
        result = await service.get_license(license_id)
        return LicenseSchema.model_validate(result.model_dump())
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.patch("/{licenseId}", response_model=LicenseSchema)
async def update_license(
    payload: LicenseUpdateSchema,
    license_id: UUID = Path(..., alias="licenseId"),
    uow: UnitOfWork = Depends(get_uow),
) -> LicenseSchema:
    """Update a license."""
    service = LicensesService(uow)
    try:
        result = await service.update_license(
            license_id,
            ServiceLicenseUpdateDto.model_validate(payload.model_dump()),
        )
        await audit_event(
            uow,
            action="licenses.update",
            entity_type="license",
            entity_id=str(license_id),
            summary=f"Updated license {result.license_key}",
            metadata={"updated_fields": list(payload.model_dump(exclude_unset=True))},
        )
        return LicenseSchema.model_validate(result.model_dump())
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/{licenseId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_license(
    license_id: UUID = Path(..., alias="licenseId"),
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    """Delete a license."""
    service = LicensesService(uow)
    try:
        await service.delete_license(license_id)
        await audit_event(
            uow,
            action="licenses.delete",
            entity_type="license",
            entity_id=str(license_id),
            summary=f"Deleted license {license_id}",
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{licenseId}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_license_via_get(
    license_id: UUID = Path(..., alias="licenseId"),
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    """Delete a license using a GET endpoint, mirroring the .NET controller action."""
    await delete_license(license_id, uow)
