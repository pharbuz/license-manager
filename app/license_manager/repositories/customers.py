from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.license_manager.db.models import Customer
from app.license_manager.repositories.base import BaseRepository


class CustomersRepository(BaseRepository[Customer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Customer)

    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        stmt = select(Customer).where(Customer.id == customer_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_by_symbol(self, customer_symbol: str) -> Customer | None:
        stmt = select(Customer).where(Customer.customer_symbol == customer_symbol)
        res = await self.session.execute(stmt)
        return res.scalars().first()
