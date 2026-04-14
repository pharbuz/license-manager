from __future__ import annotations

from unittest.mock import AsyncMock

from app.license_manager.services.models.audit import AuditLogCreate
from app.license_manager.tasks.workers import audit as audit_worker


def test_record_audit_log_task_runs_persist(monkeypatch) -> None:
    persist_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(audit_worker, "_persist_audit_log", persist_mock)

    audit_worker.record_audit_log.run(
        payload=AuditLogCreate(
            action="licenses.update",
            entity_type="license",
            entity_id="abc",
            summary="Updated license",
        )
    )

    persist_mock.assert_awaited_once()
