from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.license_manager.db.models import AuditLogEntry
from app.license_manager.repositories.base import BaseRepository


class AuditLogsRepository(BaseRepository[AuditLogEntry]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuditLogEntry)

    async def count_for_dashboard(self) -> int:
        stmt = select(func.count(AuditLogEntry.id))
        return int((await self.session.execute(stmt)).scalar_one())

    async def get_latest_occurred_at_for_dashboard(self) -> datetime | None:
        stmt = select(AuditLogEntry.occurred_at).order_by(
            AuditLogEntry.occurred_at.desc()
        )
        return (await self.session.execute(stmt)).scalars().first()
