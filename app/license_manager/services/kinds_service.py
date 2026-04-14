from __future__ import annotations

from uuid import UUID

from app.license_manager.db.models import Kind
from app.license_manager.services.base_service import BaseService
from app.license_manager.services.errors import EntityNotFoundError
from app.license_manager.services.models.kinds import (
    KindCreateDto,
    KindDto,
    KindUpdateDto,
)
from app.license_manager.uow import UnitOfWork


class KindsService(BaseService):
    def __init__(self, uow: UnitOfWork) -> None:
        super().__init__(uow)

    async def create_kind(self, payload: KindCreateDto) -> KindDto:
        entity = Kind(name=payload.name)
        await self.uow.kinds.add(entity)
        await self.commit()
        await self.uow.kinds.refresh(entity)
        return KindDto.model_validate(entity.model_dump())

    async def list_kinds(self) -> list[KindDto]:
        entities = await self.uow.kinds.list_all()
        return [KindDto.model_validate(entity.model_dump()) for entity in entities]

    async def get_kind(self, kind_id: UUID) -> KindDto:
        entity = await self.uow.kinds.get_by_id(kind_id)
        if entity is None:
            raise EntityNotFoundError(f"Kind {kind_id} not found")
        return KindDto.model_validate(entity.model_dump())

    async def update_kind(self, kind_id: UUID, payload: KindUpdateDto) -> KindDto:
        entity = await self.uow.kinds.get_by_id(kind_id)
        if entity is None:
            raise EntityNotFoundError(f"Kind {kind_id} not found")

        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(entity, field, value)

        if updates:
            await self.uow.kinds.save(entity)
            await self.commit()
            await self.uow.kinds.refresh(entity)

        return KindDto.model_validate(entity.model_dump())

    async def delete_kind(self, kind_id: UUID) -> None:
        entity = await self.uow.kinds.get_by_id(kind_id)
        if entity is None:
            raise EntityNotFoundError(f"Kind {kind_id} not found")
        await self.uow.kinds.delete(entity)
        await self.commit()
