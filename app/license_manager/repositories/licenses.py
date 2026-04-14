from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, cast, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.license_manager.db.models import Customer, License, Product
from app.license_manager.repositories.base import BaseRepository


class LicensesRepository(BaseRepository[License]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, License)

    async def get_by_id(self, license_id: UUID) -> License | None:
        stmt = select(License).where(License.id == license_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_by_license_key(self, license_key: str) -> License | None:
        stmt = select(License).where(License.license_key == license_key)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_by_customer_id(self, customer_id: UUID) -> list[License]:
        stmt = select(License).where(License.customer_id == customer_id)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_with_customer_and_product(
        self,
        license_id: UUID,
    ) -> tuple[License, Customer | None, Product | None] | None:
        stmt = (
            select(License, Customer, Product)
            .join(Customer, License.customer_id == Customer.id, isouter=True)
            .join(Product, License.product_id == Product.id, isouter=True)
            .where(License.id == license_id)
        )
        row = (await self.session.execute(stmt)).first()
        return None if row is None else tuple(row)

    async def list_expiring_with_customer_and_product(
        self,
        target_date: date,
    ) -> list[tuple[License, Customer | None, Product | None]]:
        stmt = (
            select(License, Customer, Product)
            .join(Customer, License.customer_id == Customer.id, isouter=True)
            .join(Product, License.product_id == Product.id, isouter=True)
            .where(
                License.license_state == "Active",
                cast(License.end_date, Date) == target_date,
            )
        )
        return list((await self.session.execute(stmt)).all())

    async def archive_expired(self, threshold: datetime) -> int:
        stmt = (
            update(License)
            .where(
                License.license_state == "Active",
                License.end_date < threshold,
            )
            .values(license_state="Archived")
        )
        execution = await self.session.execute(stmt)
        return execution.rowcount or 0

    async def list_active_app_package_notification_targets(
        self,
    ) -> list[tuple[License, Customer]]:
        stmt = (
            select(License, Customer)
            .join(Customer, License.customer_id == Customer.id)
            .join(Product, License.product_id == Product.id)
            .where(
                License.license_state == "Active",
                Product.name == "AppPackage",
                Customer.notifications_enabled.is_(True),
            )
        )
        return list((await self.session.execute(stmt)).all())
