from __future__ import annotations

from uuid import UUID

from app.license_manager.db.models import Customer
from app.license_manager.services.base_service import BaseService
from app.license_manager.services.errors import EntityNotFoundError
from app.license_manager.services.models.customers import (
    CustomerCreateDto,
    CustomerDto,
    CustomerUpdateDto,
)
from app.license_manager.uow import UnitOfWork


class CustomersService(BaseService):
    def __init__(self, uow: UnitOfWork) -> None:
        super().__init__(uow)

    async def create_customer(self, payload: CustomerCreateDto) -> CustomerDto:
        entity = Customer(
            name=payload.name,
            email=str(payload.email),
            customer_symbol=payload.customer_symbol,
            notifications_enabled=payload.notifications_enabled,
            gem_fury_used=payload.gem_fury_used,
            contact_person_name=payload.contact_person_name,
            contact_person_phone=payload.contact_person_phone,
        )
        await self.uow.customers.add(entity)
        await self.commit()
        await self.uow.customers.refresh(entity)
        return CustomerDto.model_validate(entity.model_dump())

    async def list_customers(self) -> list[CustomerDto]:
        entities = await self.uow.customers.list_all()
        return [CustomerDto.model_validate(entity.model_dump()) for entity in entities]

    async def get_customer(self, customer_id: UUID) -> CustomerDto:
        entity = await self.uow.customers.get_by_id(customer_id)
        if entity is None:
            raise EntityNotFoundError(f"Customer {customer_id} not found")
        return CustomerDto.model_validate(entity.model_dump())

    async def update_customer(
        self,
        customer_id: UUID,
        payload: CustomerUpdateDto,
    ) -> CustomerDto:
        entity = await self.uow.customers.get_by_id(customer_id)
        if entity is None:
            raise EntityNotFoundError(f"Customer {customer_id} not found")

        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(entity, field, value)

        if updates:
            await self.uow.customers.save(entity)
            await self.commit()
            await self.uow.customers.refresh(entity)

        return CustomerDto.model_validate(entity.model_dump())

    async def delete_customer(self, customer_id: UUID) -> None:
        entity = await self.uow.customers.get_by_id(customer_id)
        if entity is None:
            raise EntityNotFoundError(f"Customer {customer_id} not found")
        await self.uow.customers.delete(entity)
        await self.commit()
