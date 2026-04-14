from __future__ import annotations

from app.license_manager.uow import UnitOfWork


class BaseService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def commit(self) -> None:
        await self.uow.commit()

    async def rollback(self) -> None:
        await self.uow.rollback()
