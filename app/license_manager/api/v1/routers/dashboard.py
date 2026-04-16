from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.license_manager.api.dependencies import get_uow
from app.license_manager.api.v1.schemas.dashboard import DashboardSchema
from app.license_manager.services.dashboard_service import DashboardService
from app.license_manager.uow import UnitOfWork

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard", response_model=DashboardSchema)
async def get_dashboard(
    request: Request,
    uow: UnitOfWork = Depends(get_uow),
) -> DashboardSchema:
    service = DashboardService(uow, request.app)
    result = await service.get_dashboard()
    return DashboardSchema.model_validate(result.model_dump(mode="json"))
