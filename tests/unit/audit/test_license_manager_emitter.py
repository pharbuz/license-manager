from __future__ import annotations

import pytest

from app.license_manager.audit import audit_event
from app.license_manager.services.models.audit import AuditLogCreate


class FakeUnitOfWork:
    session = object()


@pytest.mark.asyncio
async def test_audit_event_enqueues_payload(monkeypatch) -> None:
    captured: dict[str, AuditLogCreate] = {}

    def _fake_enqueue(payload: AuditLogCreate) -> None:
        captured["payload"] = payload

    monkeypatch.setattr(
        "app.license_manager.audit.emitter.enqueue_audit_event",
        _fake_enqueue,
    )

    await audit_event(
        FakeUnitOfWork(),
        action="customers.create",
        entity_type="customer",
        entity_id="123",
        summary="Created customer",
        metadata={"name": "Acme"},
    )

    payload = captured["payload"]
    assert payload.action == "customers.create"
    assert payload.entity_type == "customer"
    assert payload.entity_id == "123"
    assert payload.summary == "Created customer"
    assert payload.metadata == {"name": "Acme"}
