from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

T = TypeVar("T")


class BaseRepository[T]:
    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def save(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def add_all(self, entities: Iterable[T]) -> None:
        self.session.add_all(list(entities))
        await self.session.flush()

    async def list_all(self) -> Sequence[T]:
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_one_by(self, column: InstrumentedAttribute, value) -> T | None:
        stmt = select(self.model).where(column == value)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)

    async def refresh(self, entity: T) -> None:
        await self.session.refresh(entity)
