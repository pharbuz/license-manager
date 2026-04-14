from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.license_manager.api.dependencies import get_uow
from app.license_manager.api.v1.schemas.audit_logs import (
    AuditLogEntrySchema,
    AuditLogQueryParams,
)
from app.license_manager.db.models import AuditLogEntry
from app.license_manager.uow import UnitOfWork

router = APIRouter(prefix="/audit", tags=["AuditLogs"])


@router.get("/logs", response_model=list[AuditLogEntrySchema])
async def list_audit_logs(
    filters: AuditLogQueryParams = Depends(),
    uow: UnitOfWork = Depends(get_uow),
) -> list[AuditLogEntrySchema]:
    if uow.session is None:
        raise RuntimeError("UnitOfWork session is not initialized")

    stmt = select(AuditLogEntry)
    if filters.entity_type:
        stmt = stmt.where(AuditLogEntry.entity_type == filters.entity_type)
    if filters.entity_id:
        stmt = stmt.where(AuditLogEntry.entity_id == filters.entity_id)
    if filters.request_id:
        stmt = stmt.where(AuditLogEntry.request_id == filters.request_id)
    if filters.actor_id:
        stmt = stmt.where(AuditLogEntry.actor_id == filters.actor_id)
    if filters.source:
        stmt = stmt.where(AuditLogEntry.source == filters.source)
    if filters.occurred_from:
        stmt = stmt.where(AuditLogEntry.occurred_at >= filters.occurred_from)
    if filters.occurred_to:
        stmt = stmt.where(AuditLogEntry.occurred_at <= filters.occurred_to)

    stmt = stmt.order_by(AuditLogEntry.recorded_at.desc())
    res = await uow.session.execute(stmt)
    rows = list(res.scalars().all())
    return [AuditLogEntrySchema.model_validate(row) for row in rows]
