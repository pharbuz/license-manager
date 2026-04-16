from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
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

    async def list_dropdown_items(self) -> list[tuple[UUID, str, str]]:
        stmt = select(Customer.id, Customer.customer_symbol, Customer.name).order_by(
            Customer.customer_symbol.asc(),
            Customer.name.asc(),
        )
        return list((await self.session.execute(stmt)).all())

    async def count_for_dashboard(self) -> int:
        stmt = select(func.count(Customer.id))
        return int((await self.session.execute(stmt)).scalar_one())
