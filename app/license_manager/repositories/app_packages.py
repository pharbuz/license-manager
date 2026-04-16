from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.license_manager.core.helpers import parse_semantic_version
from app.license_manager.db.models import AppPackage
from app.license_manager.repositories.base import BaseRepository


class AppPackagesRepository(BaseRepository[AppPackage]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AppPackage)

    async def get_by_id(self, app_package_id: UUID) -> AppPackage | None:
        stmt = select(AppPackage).where(AppPackage.id == app_package_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_by_version_number(self, version_number: str) -> AppPackage | None:
        stmt = select(AppPackage).where(AppPackage.version_number == version_number)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_max_version(self) -> str:
        stmt = select(AppPackage.version_number)
        versions = list((await self.session.execute(stmt)).scalars().all())
        if not versions:
            return "0.0.0"
        return max(versions, key=parse_semantic_version)

    async def count_for_dashboard(self) -> int:
        stmt = select(func.count(AppPackage.id))
        return int((await self.session.execute(stmt)).scalar_one())
