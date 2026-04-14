from __future__ import annotations

from uuid import UUID

from app.license_manager.db.models import AppPackage
from app.license_manager.services.base_service import BaseService
from app.license_manager.services.errors import EntityNotFoundError
from app.license_manager.services.models.app_packages import (
    AppPackageCreateDto,
    AppPackageDto,
    AppPackageUpdateDto,
)
from app.license_manager.uow import UnitOfWork


class AppPackagesService(BaseService):
    def __init__(self, uow: UnitOfWork) -> None:
        super().__init__(uow)

    async def create_app_package(self, payload: AppPackageCreateDto) -> AppPackageDto:
        entity = AppPackage(
            version_number=payload.version_number,
            binary_name=payload.binary_name,
            gem_fury_url=payload.gem_fury_url,
            binary_url=payload.binary_url,
        )
        await self.uow.app_packages.add(entity)
        await self.commit()
        await self.uow.app_packages.refresh(entity)
        return AppPackageDto.model_validate(entity.model_dump())

    async def list_app_packages(self) -> list[AppPackageDto]:
        entities = await self.uow.app_packages.list_all()
        return [
            AppPackageDto.model_validate(entity.model_dump()) for entity in entities
        ]

    async def get_app_package(self, app_package_id: UUID) -> AppPackageDto:
        entity = await self.uow.app_packages.get_by_id(app_package_id)
        if entity is None:
            raise EntityNotFoundError(f"AppPackage {app_package_id} not found")
        return AppPackageDto.model_validate(entity.model_dump())

    async def update_app_package(
        self,
        app_package_id: UUID,
        payload: AppPackageUpdateDto,
    ) -> AppPackageDto:
        entity = await self.uow.app_packages.get_by_id(app_package_id)
        if entity is None:
            raise EntityNotFoundError(f"AppPackage {app_package_id} not found")

        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(entity, field, value)

        if updates:
            await self.uow.app_packages.save(entity)
            await self.commit()
            await self.uow.app_packages.refresh(entity)

        return AppPackageDto.model_validate(entity.model_dump())

    async def delete_app_package(self, app_package_id: UUID) -> None:
        entity = await self.uow.app_packages.get_by_id(app_package_id)
        if entity is None:
            raise EntityNotFoundError(f"AppPackage {app_package_id} not found")
        await self.uow.app_packages.delete(entity)
        await self.commit()
