from __future__ import annotations

from uuid import UUID

from sqlalchemy import cast, desc, select, update
from sqlalchemy.dialects.postgresql import JSONPATH
from sqlalchemy.ext.asyncio import AsyncSession

from app.license_manager.db.models import Setting
from app.license_manager.repositories.base import BaseRepository


class SettingsRepository(BaseRepository[Setting]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Setting)

    async def get_by_object_id(self, object_id: UUID) -> Setting | None:
        stmt = select(Setting).where(Setting.object_id == object_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_by_schema_and_scope(
        self,
        *,
        schema_id: str,
        scope: str | None,
    ) -> list[Setting]:
        stmt = select(Setting).where(
            Setting.schema_id == schema_id,
            Setting.scope == scope,
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def list_by_schema_and_scope_prefix(
        self,
        *,
        schema_id: str,
        scope_prefix: str,
    ) -> list[Setting]:
        stmt = select(Setting).where(
            Setting.schema_id == schema_id,
            Setting.scope.like(f"{scope_prefix}%"),
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def list_by_scope_prefix_and_json_path(
        self,
        *,
        schema_id: str,
        scope_prefix: str,
        json_path: str | None = None,
    ) -> list[Setting]:
        stmt = select(Setting).where(
            Setting.schema_id == schema_id,
            Setting.scope.like(f"{scope_prefix}%"),
        )
        if json_path is not None:
            stmt = stmt.where(Setting.value.op("@?")(cast(json_path, JSONPATH)))
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_latest_by_schema_and_scope(
        self,
        *,
        schema_id: str,
        scope: str | None,
        for_update: bool = False,
    ) -> Setting | None:
        stmt = (
            select(Setting)
            .where(Setting.schema_id == schema_id, Setting.scope == scope)
            .order_by(desc(Setting.created_at))
            .limit(1)
        )
        if for_update:
            stmt = stmt.with_for_update()
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_by_value_json_path(self, json_path: str) -> list[Setting]:
        stmt = select(Setting).where(Setting.value.op("@?")(cast(json_path, JSONPATH)))
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update(self, object_id: UUID, **fields) -> Setting | None:
        if not fields:
            return await self.get_by_object_id(object_id)
        stmt = (
            update(Setting)
            .where(Setting.object_id == object_id)
            .values(**fields)
            .returning(Setting)
        )
        res = await self.session.execute(stmt)
        row = res.fetchone()
        entity = row[0] if row and not isinstance(row, Setting) else row
        if isinstance(entity, Setting):
            return entity
        return await self.get_by_object_id(object_id)

    async def delete_by_schema_and_scope(
        self,
        *,
        schema_id: str,
        scope: str | None,
    ) -> int:
        rows = await self.list_by_schema_and_scope(schema_id=schema_id, scope=scope)
        for row in rows:
            await self.delete(row)
        return len(rows)
