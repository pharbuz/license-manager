from __future__ import annotations

import asyncio
from typing import Any

from celery import shared_task
from pydantic import ValidationError

from app.license_manager.db.models import AuditLogEntry
from app.license_manager.observability.logging import get_logger
from app.license_manager.services.models.audit import AuditLogCreate
from app.license_manager.tasks.workers.helpers import new_uow

logger = get_logger(__name__)


async def _persist_audit_log(payload: AuditLogCreate) -> None:
    async with new_uow() as uow:
        entry = AuditLogEntry(
            actor_id=payload.actor_id,
            actor_type=payload.actor_type.value,
            actor_display_name=payload.actor_display_name,
            source=payload.source,
            request_id=payload.request_id,
            action=payload.action,
            entity_type=payload.entity_type,
            entity_id=payload.entity_id,
            summary=payload.summary,
            diff=payload.diff,
            context=payload.metadata,
            occurred_at=payload.occurred_at,
        )
        await uow.audit_logs.add(entry)
        await uow.commit()


@shared_task(
    bind=True,
    name="app.license_manager.tasks.workers.audit.record_audit_log",
    pydantic=True,
)
def record_audit_log(self, payload: AuditLogCreate) -> None:
    raw_payload: Any = payload
    try:
        payload_obj = AuditLogCreate.model_validate(payload)
    except ValidationError as exc:
        logger.error(
            "Invalid audit log payload",
            extra={"payload": raw_payload, "errors": exc.errors()},
        )
        return

    try:
        asyncio.run(_persist_audit_log(payload_obj))
    except Exception as exc:
        logger.exception(
            "Audit log task execution failed",
            extra={
                "payload": payload_obj.model_dump(by_alias=True, mode="json"),
                "error": str(exc),
            },
        )
        raise
