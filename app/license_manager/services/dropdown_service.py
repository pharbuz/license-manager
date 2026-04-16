from __future__ import annotations

from app.license_manager.services.base_service import BaseService
from app.license_manager.services.models.dropdowns import DropdownItemDto, DropdownType
from app.license_manager.uow import UnitOfWork


class DropdownService(BaseService):
    def __init__(self, uow: UnitOfWork) -> None:
        super().__init__(uow)

    async def get_dropdown_items(
        self,
        dropdown_type: DropdownType,
    ) -> list[DropdownItemDto]:
        if dropdown_type == DropdownType.CUSTOMER:
            items = await self.uow.customers.list_dropdown_items()
            return [
                DropdownItemDto(id=item_id, text=f"{customer_symbol} - {name}")
                for item_id, customer_symbol, name in items
            ]

        if dropdown_type == DropdownType.LICENSE_KIND:
            items = await self.uow.kinds.list_dropdown_items()
            return [DropdownItemDto(id=item_id, text=name) for item_id, name in items]

        items = await self.uow.products.list_dropdown_items()
        return [DropdownItemDto(id=item_id, text=name) for item_id, name in items]
