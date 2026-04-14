from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.license_manager.db.models import AuditLogEntry
from app.license_manager.repositories.base import BaseRepository


class AuditLogsRepository(BaseRepository[AuditLogEntry]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuditLogEntry)
