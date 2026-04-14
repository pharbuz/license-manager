from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.license_manager.db.models import Kind
from app.license_manager.repositories.base import BaseRepository


class KindsRepository(BaseRepository[Kind]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Kind)

    async def get_by_id(self, kind_id: UUID) -> Kind | None:
        stmt = select(Kind).where(Kind.id == kind_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_by_name(self, name: str) -> Kind | None:
        stmt = select(Kind).where(Kind.name == name)
        res = await self.session.execute(stmt)
        return res.scalars().first()
