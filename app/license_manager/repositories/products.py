from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.license_manager.db.models import Product
from app.license_manager.repositories.base import BaseRepository


class ProductsRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Product)

    async def get_by_id(self, product_id: UUID) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_by_name(self, name: str) -> Product | None:
        stmt = select(Product).where(Product.name == name)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_dropdown_items(self) -> list[tuple[UUID, str]]:
        stmt = select(Product.id, Product.name).order_by(Product.name.asc())
        return list((await self.session.execute(stmt)).all())

    async def count_for_dashboard(self) -> int:
        stmt = select(func.count(Product.id))
        return int((await self.session.execute(stmt)).scalar_one())
