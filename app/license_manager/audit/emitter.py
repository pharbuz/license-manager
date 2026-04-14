from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.license_manager.observability.logging import get_logger
from app.license_manager.services.models.audit import AuditActorType, AuditLogCreate
from app.license_manager.uow import UnitOfWork

logger = get_logger(__name__)


def enqueue_audit_event(payload: AuditLogCreate | dict[str, Any]) -> None:
    data = (
        payload.model_dump(by_alias=True, mode="json")
        if isinstance(payload, AuditLogCreate)
        else payload
    )
    try:
        from app.license_manager.tasks.workers.audit import record_audit_log

        record_audit_log.delay(data)
    except Exception as exc:
        logger.exception(
            "Failed to enqueue audit log event",
            extra={"payload": data, "error": str(exc)},
        )


async def audit_event(
    uow: UnitOfWork,
    *,
    action: str,
    entity_type: str,
    entity_id: str,
    summary: str | None = None,
    diff: list[dict[str, Any]] | dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    actor_id: str | None = None,
    actor_type: str = "system",
    actor_display_name: str | None = None,
    source: str = "api",
    request_id: str | None = None,
    occurred_at: datetime | None = None,
) -> None:
    del uow

    payload = AuditLogCreate(
        actor_id=actor_id,
        actor_type=AuditActorType(actor_type),
        actor_display_name=actor_display_name,
        source=source,
        request_id=request_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        summary=summary,
        diff=diff,
        metadata=metadata,
        occurred_at=occurred_at or datetime.now(tz=UTC),
    )
    enqueue_audit_event(payload)
