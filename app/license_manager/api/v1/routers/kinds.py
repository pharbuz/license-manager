from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.license_manager.api.dependencies import get_uow
from app.license_manager.api.v1.schemas.kinds import (
    KindCreateSchema,
    KindSchema,
    KindUpdateSchema,
)
from app.license_manager.audit import audit_event
from app.license_manager.services.errors import EntityNotFoundError
from app.license_manager.services.kinds_service import KindsService
from app.license_manager.services.models.kinds import (
    KindCreateDto as ServiceKindCreateDto,
)
from app.license_manager.services.models.kinds import (
    KindUpdateDto as ServiceKindUpdateDto,
)
from app.license_manager.uow import UnitOfWork

router = APIRouter(prefix="/kinds", tags=["Kinds"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=KindSchema)
async def create_kind(
    payload: KindCreateSchema,
    uow: UnitOfWork = Depends(get_uow),
) -> KindSchema:
    """Create a new kind."""
    service = KindsService(uow)
    result = await service.create_kind(
        ServiceKindCreateDto.model_validate(payload.model_dump())
    )
    await audit_event(
        uow,
        action="kinds.create",
        entity_type="kind",
        entity_id=str(result.id),
        summary=f"Created kind {result.name}",
    )
    return KindSchema.model_validate(result.model_dump())


@router.get("", response_model=list[KindSchema])
async def list_kinds(
    uow: UnitOfWork = Depends(get_uow),
) -> list[KindSchema]:
    """List all kinds."""
    service = KindsService(uow)
    result = await service.list_kinds()
    return [KindSchema.model_validate(item.model_dump()) for item in result]


@router.get("/{kindId}", response_model=KindSchema)
async def get_kind(
    kind_id: UUID = Path(..., alias="kindId"),
    uow: UnitOfWork = Depends(get_uow),
) -> KindSchema:
    """Get a kind by ID."""
    service = KindsService(uow)
    try:
        result = await service.get_kind(kind_id)
        return KindSchema.model_validate(result.model_dump())
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.patch("/{kindId}", response_model=KindSchema)
async def update_kind(
    payload: KindUpdateSchema,
    kind_id: UUID = Path(..., alias="kindId"),
    uow: UnitOfWork = Depends(get_uow),
) -> KindSchema:
    """Update a kind."""
    service = KindsService(uow)
    try:
        result = await service.update_kind(
            kind_id,
            ServiceKindUpdateDto.model_validate(payload.model_dump()),
        )
        await audit_event(
            uow,
            action="kinds.update",
            entity_type="kind",
            entity_id=str(kind_id),
            summary=f"Updated kind {result.name}",
            metadata={"updated_fields": list(payload.model_dump(exclude_unset=True))},
        )
        return KindSchema.model_validate(result.model_dump())
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/{kindId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kind(
    kind_id: UUID = Path(..., alias="kindId"),
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    """Delete a kind."""
    service = KindsService(uow)
    try:
        await service.delete_kind(kind_id)
        await audit_event(
            uow,
            action="kinds.delete",
            entity_type="kind",
            entity_id=str(kind_id),
            summary=f"Deleted kind {kind_id}",
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
