from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.license_manager.services.dropdown_service import DropdownService
from app.license_manager.services.models.dropdowns import DropdownType


class FakeDropdownUnitOfWork:
    def __init__(self) -> None:
        self.customers = MagicMock()
        self.customers.list_dropdown_items = AsyncMock(return_value=[])
        self.kinds = MagicMock()
        self.kinds.list_dropdown_items = AsyncMock(return_value=[])
        self.products = MagicMock()
        self.products.list_dropdown_items = AsyncMock(return_value=[])


@pytest.mark.asyncio
async def test_dropdown_service_formats_customer_options() -> None:
    customer_id = uuid4()
    uow = FakeDropdownUnitOfWork()
    uow.customers.list_dropdown_items.return_value = [
        (customer_id, "ACM", "Acme"),
    ]

    service = DropdownService(uow)

    result = await service.get_dropdown_items(DropdownType.CUSTOMER)

    assert result[0].id == customer_id
    assert result[0].text == "ACM - Acme"


@pytest.mark.asyncio
async def test_dropdown_service_returns_kind_options() -> None:
    kind_id = uuid4()
    uow = FakeDropdownUnitOfWork()
    uow.kinds.list_dropdown_items.return_value = [(kind_id, "Trial")]

    service = DropdownService(uow)

    result = await service.get_dropdown_items(DropdownType.LICENSE_KIND)

    assert result[0].id == kind_id
    assert result[0].text == "Trial"
