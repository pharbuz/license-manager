from __future__ import annotations

from uuid import UUID

from app.license_manager.db.models import Product
from app.license_manager.services.base_service import BaseService
from app.license_manager.services.errors import EntityNotFoundError
from app.license_manager.services.models.products import (
    ProductCreateDto,
    ProductDto,
    ProductUpdateDto,
)
from app.license_manager.uow import UnitOfWork


class ProductsService(BaseService):
    def __init__(self, uow: UnitOfWork) -> None:
        super().__init__(uow)

    async def create_product(self, payload: ProductCreateDto) -> ProductDto:
        entity = Product(
            name=payload.name,
            kind=payload.kind,
        )
        await self.uow.products.add(entity)
        await self.commit()
        await self.uow.products.refresh(entity)
        return ProductDto.model_validate(entity.model_dump())

    async def list_products(self) -> list[ProductDto]:
        entities = await self.uow.products.list_all()
        return [ProductDto.model_validate(entity.model_dump()) for entity in entities]

    async def get_product(self, product_id: UUID) -> ProductDto:
        entity = await self.uow.products.get_by_id(product_id)
        if entity is None:
            raise EntityNotFoundError(f"Product {product_id} not found")
        return ProductDto.model_validate(entity.model_dump())

    async def update_product(
        self,
        product_id: UUID,
        payload: ProductUpdateDto,
    ) -> ProductDto:
        entity = await self.uow.products.get_by_id(product_id)
        if entity is None:
            raise EntityNotFoundError(f"Product {product_id} not found")

        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(entity, field, value)

        if updates:
            await self.uow.products.save(entity)
            await self.commit()
            await self.uow.products.refresh(entity)

        return ProductDto.model_validate(entity.model_dump())

    async def delete_product(self, product_id: UUID) -> None:
        entity = await self.uow.products.get_by_id(product_id)
        if entity is None:
            raise EntityNotFoundError(f"Product {product_id} not found")
        await self.uow.products.delete(entity)
        await self.commit()
