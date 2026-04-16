from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.license_manager.api.dependencies import get_uow
from app.license_manager.api.v1.schemas.dropdowns import (
    DropdownItemSchema,
    DropdownQuerySchema,
)
from app.license_manager.services.dropdown_service import DropdownService
from app.license_manager.uow import UnitOfWork

router = APIRouter(tags=["Dropdown"])


@router.get("/dropdown", response_model=list[DropdownItemSchema])
async def get_dropdown(
    dropdown_type: str = Query(..., alias="type"),
    uow: UnitOfWork = Depends(get_uow),
) -> list[DropdownItemSchema]:
    try:
        query = DropdownQuerySchema(type=dropdown_type)
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc

    service = DropdownService(uow)
    result = await service.get_dropdown_items(query.type)
    return [DropdownItemSchema.model_validate(item.model_dump()) for item in result]
