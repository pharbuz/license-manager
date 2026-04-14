from __future__ import annotations

from app.license_manager.db.models import AuditLogEntry


def test_audit_log_entry_mapping() -> None:
    table = AuditLogEntry.__table__

    assert table.schema == "licensemanager"
    assert table.name == "audit_log_entries"
    assert table.c.action.type.length == 128
    assert table.c.entity_type.type.length == 255
    assert table.c.entity_id.type.length == 255
    assert table.c.recorded_at.server_default is not None
