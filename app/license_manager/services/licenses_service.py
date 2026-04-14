from __future__ import annotations

from uuid import UUID

from kombu.exceptions import OperationalError

from app.license_manager.db.models import License
from app.license_manager.services.base_service import BaseService
from app.license_manager.services.email_background_jobs_service import (
    EmailBackgroundJobsService,
)
from app.license_manager.services.errors import EntityNotFoundError
from app.license_manager.services.models.background_jobs import (
    InitialLicenseNotificationTaskPayload,
)
from app.license_manager.services.models.licenses import (
    LicenseCreateDto,
    LicenseDto,
    LicenseUpdateDto,
)
from app.license_manager.tasks.workers.email_background_jobs import (
    enqueue_initial_license_notification_job,
)
from app.license_manager.uow import UnitOfWork


class LicensesService(BaseService):
    def __init__(self, uow: UnitOfWork) -> None:
        super().__init__(uow)

    async def create_license(self, payload: LicenseCreateDto) -> LicenseDto:
        entity = License(
            customer_id=payload.customer_id,
            product_id=payload.product_id,
            kind_id=payload.kind_id,
            license_count=payload.license_count,
            license_state=payload.license_state,
            license_key=payload.license_key,
            license_email=str(payload.license_email),
            double_send=payload.double_send,
            begin_date=payload.begin_date,
            end_date=payload.end_date,
            notification_date=payload.notification_date,
        )
        await self.uow.licenses.add(entity)
        await self.commit()
        await self.uow.licenses.refresh(entity)
        await self._trigger_initial_notification(entity)
        return LicenseDto.model_validate(entity.model_dump())

    async def list_licenses(self) -> list[LicenseDto]:
        entities = await self.uow.licenses.list_all()
        return [LicenseDto.model_validate(entity.model_dump()) for entity in entities]

    async def list_licenses_by_customer(self, customer_id: UUID) -> list[LicenseDto]:
        entities = await self.uow.licenses.list_by_customer_id(customer_id)
        return [LicenseDto.model_validate(entity.model_dump()) for entity in entities]

    async def get_license(self, license_id: UUID) -> LicenseDto:
        entity = await self.uow.licenses.get_by_id(license_id)
        if entity is None:
            raise EntityNotFoundError(f"License {license_id} not found")
        return LicenseDto.model_validate(entity.model_dump())

    async def update_license(
        self,
        license_id: UUID,
        payload: LicenseUpdateDto,
    ) -> LicenseDto:
        entity = await self.uow.licenses.get_by_id(license_id)
        if entity is None:
            raise EntityNotFoundError(f"License {license_id} not found")

        updates = payload.model_dump(exclude_unset=True)
        if "license_email" in updates and updates["license_email"] is not None:
            updates["license_email"] = str(updates["license_email"])

        for field, value in updates.items():
            setattr(entity, field, value)

        if updates:
            await self.uow.licenses.save(entity)
            await self.commit()
            await self.uow.licenses.refresh(entity)

        return LicenseDto.model_validate(entity.model_dump())

    async def delete_license(self, license_id: UUID) -> None:
        entity = await self.uow.licenses.get_by_id(license_id)
        if entity is None:
            raise EntityNotFoundError(f"License {license_id} not found")
        await self.uow.licenses.delete(entity)
        await self.commit()

    async def _trigger_initial_notification(self, entity: License) -> None:
        if entity.customer_id is None or entity.product_id is None:
            return

        customer = await self.uow.customers.get_by_id(entity.customer_id)
        product = await self.uow.products.get_by_id(entity.product_id)
        if customer is None or product is None:
            return
        if not customer.notifications_enabled or product.name.lower() != "apppackage":
            return

        payload = InitialLicenseNotificationTaskPayload(license_id=entity.id)
        try:
            enqueue_initial_license_notification_job(payload)
        except OperationalError:
            service = EmailBackgroundJobsService(self.uow)
            await service.send_initial_license_notification(payload)
