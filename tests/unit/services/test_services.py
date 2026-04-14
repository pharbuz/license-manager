from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from kombu.exceptions import OperationalError

from app.license_manager.db.models import Customer, License, Product
from app.license_manager.services.customers_service import CustomersService
from app.license_manager.services.errors import EntityNotFoundError
from app.license_manager.services.licenses_service import LicensesService
from app.license_manager.services.models.background_jobs import (
    InitialLicenseNotificationTaskPayload,
)
from app.license_manager.services.models.customers import (
    CustomerCreateDto,
    CustomerUpdateDto,
)
from app.license_manager.services.models.licenses import LicenseCreateDto
from app.license_manager.services.models.products import ProductUpdateDto
from app.license_manager.services.products_service import ProductsService


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.session = MagicMock()
        self.session.refresh = AsyncMock(side_effect=self._refresh_entity)

        self.commit = AsyncMock()
        self.rollback = AsyncMock()

        self.customers = MagicMock()
        self.customers.add = AsyncMock()
        self.customers.save = AsyncMock()
        self.customers.refresh = AsyncMock(side_effect=self._refresh_entity)
        self.customers.get_by_id = AsyncMock(return_value=None)
        self.customers.list_all = AsyncMock(return_value=[])
        self.customers.delete = AsyncMock()

        self.licenses = MagicMock()
        self.licenses.add = AsyncMock()
        self.licenses.save = AsyncMock()
        self.licenses.refresh = AsyncMock(side_effect=self._refresh_entity)
        self.licenses.get_by_id = AsyncMock(return_value=None)
        self.licenses.list_all = AsyncMock(return_value=[])
        self.licenses.list_by_customer_id = AsyncMock(return_value=[])
        self.licenses.delete = AsyncMock()

        self.products = MagicMock()
        self.products.add = AsyncMock()
        self.products.save = AsyncMock()
        self.products.refresh = AsyncMock(side_effect=self._refresh_entity)
        self.products.get_by_id = AsyncMock(return_value=None)
        self.products.list_all = AsyncMock(return_value=[])
        self.products.delete = AsyncMock()

        self.kinds = MagicMock()
        self.kinds.add = AsyncMock()
        self.kinds.save = AsyncMock()
        self.kinds.refresh = AsyncMock(side_effect=self._refresh_entity)
        self.kinds.get_by_id = AsyncMock(return_value=None)
        self.kinds.list_all = AsyncMock(return_value=[])
        self.kinds.delete = AsyncMock()
        self.app_packages = MagicMock()
        self.app_packages.add = AsyncMock()
        self.app_packages.save = AsyncMock()
        self.app_packages.refresh = AsyncMock(side_effect=self._refresh_entity)
        self.app_packages.get_by_id = AsyncMock(return_value=None)
        self.app_packages.list_all = AsyncMock(return_value=[])
        self.app_packages.delete = AsyncMock()
        self.audit_logs = MagicMock()

    async def _refresh_entity(self, entity) -> None:
        if entity.id is None:
            entity.id = uuid4()
        if getattr(entity, "created_at", None) is None:
            entity.created_at = datetime(2026, 1, 1, 0, 0, 0)
        if getattr(entity, "modified_at", None) is None:
            entity.modified_at = datetime(2026, 1, 1, 0, 0, 0)


@pytest.fixture
def fake_uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.mark.asyncio
async def test_customers_service_create_customer(fake_uow: FakeUnitOfWork) -> None:
    service = CustomersService(fake_uow)

    payload = CustomerCreateDto(
        name="Acme",
        email="acme@example.com",
        customer_symbol="ACM",
    )

    result = await service.create_customer(payload)

    fake_uow.customers.add.assert_awaited_once()
    fake_uow.commit.assert_awaited_once()
    fake_uow.customers.refresh.assert_awaited_once()
    assert result.name == "Acme"
    assert result.customer_symbol == "ACM"


@pytest.mark.asyncio
async def test_customers_service_get_customer_not_found(
    fake_uow: FakeUnitOfWork,
) -> None:
    service = CustomersService(fake_uow)

    with pytest.raises(EntityNotFoundError):
        await service.get_customer(uuid4())


@pytest.mark.asyncio
async def test_licenses_service_create_and_list_by_customer(
    fake_uow: FakeUnitOfWork,
) -> None:
    service = LicensesService(fake_uow)

    customer_id = uuid4()
    payload = LicenseCreateDto(
        customer_id=customer_id,
        product_id=None,
        kind_id=None,
        license_count=5,
        license_state="active",
        license_key="key-123",
        license_email="owner@example.com",
        begin_date=datetime(2026, 1, 1, 0, 0, 0),
        end_date=datetime(2026, 12, 31, 0, 0, 0),
        notification_date=datetime(2026, 12, 1, 0, 0, 0),
    )

    created = await service.create_license(payload)

    fake_uow.licenses.add.assert_awaited_once()
    fake_uow.commit.assert_awaited_once()
    assert created.license_key == "key-123"

    entity = License(
        id=uuid4(),
        customer_id=customer_id,
        product_id=None,
        kind_id=None,
        license_count=1,
        license_state="active",
        license_key="k",
        license_email="owner@example.com",
        double_send=False,
        begin_date=datetime(2026, 1, 1, 0, 0, 0),
        end_date=datetime(2026, 1, 2, 0, 0, 0),
        notification_date=datetime(2026, 1, 1, 0, 0, 0),
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )
    fake_uow.licenses.list_by_customer_id.return_value = [entity]

    rows = await service.list_licenses_by_customer(customer_id)

    assert len(rows) == 1
    assert rows[0].customer_id == customer_id


@pytest.mark.asyncio
async def test_licenses_service_create_license_enqueues_initial_notification(
    fake_uow: FakeUnitOfWork,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LicensesService(fake_uow)
    customer_id = uuid4()
    product_id = uuid4()

    fake_uow.customers.get_by_id.return_value = Customer(
        id=customer_id,
        name="Acme",
        email="customer@example.com",
        notifications_enabled=True,
        gem_fury_used=True,
        customer_symbol="ACM",
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )
    fake_uow.products.get_by_id.return_value = Product(
        id=product_id,
        name="AppPackage",
        kind="Agent",
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )

    enqueued_payloads: list[InitialLicenseNotificationTaskPayload] = []
    monkeypatch.setattr(
        "app.license_manager.services.licenses_service.enqueue_initial_license_notification_job",
        lambda payload: enqueued_payloads.append(payload),
    )

    payload = LicenseCreateDto(
        customer_id=customer_id,
        product_id=product_id,
        kind_id=None,
        license_count=5,
        license_state="Active",
        license_key="key-123",
        license_email="owner@example.com",
        double_send=True,
        begin_date=datetime(2026, 1, 1, 0, 0, 0),
        end_date=datetime(2026, 12, 31, 0, 0, 0),
        notification_date=datetime(1970, 1, 1, 0, 0, 0),
    )

    created = await service.create_license(payload)

    assert created.license_key == "key-123"
    assert len(enqueued_payloads) == 1
    assert enqueued_payloads[0].license_id == created.id


@pytest.mark.asyncio
async def test_licenses_service_create_license_falls_back_when_queue_unavailable(
    fake_uow: FakeUnitOfWork,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LicensesService(fake_uow)
    customer_id = uuid4()
    product_id = uuid4()

    fake_uow.customers.get_by_id.return_value = Customer(
        id=customer_id,
        name="Acme",
        email="customer@example.com",
        notifications_enabled=True,
        gem_fury_used=True,
        customer_symbol="ACM",
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )
    fake_uow.products.get_by_id.return_value = Product(
        id=product_id,
        name="AppPackage",
        kind="Agent",
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )

    monkeypatch.setattr(
        "app.license_manager.services.licenses_service.enqueue_initial_license_notification_job",
        lambda _payload: (_ for _ in ()).throw(OperationalError("queue unavailable")),
    )
    fallback_send = AsyncMock(return_value=None)
    fallback_service = MagicMock()
    fallback_service.send_initial_license_notification = fallback_send
    monkeypatch.setattr(
        "app.license_manager.services.licenses_service.EmailBackgroundJobsService",
        lambda _uow: fallback_service,
    )

    await service.create_license(
        LicenseCreateDto(
            customer_id=customer_id,
            product_id=product_id,
            kind_id=None,
            license_count=5,
            license_state="Active",
            license_key="key-123",
            license_email="owner@example.com",
            double_send=False,
            begin_date=datetime(2026, 1, 1, 0, 0, 0),
            end_date=datetime(2026, 12, 31, 0, 0, 0),
            notification_date=datetime(1970, 1, 1, 0, 0, 0),
        )
    )

    fallback_send.assert_awaited_once()


@pytest.mark.asyncio
async def test_products_service_update_product(fake_uow: FakeUnitOfWork) -> None:
    service = ProductsService(fake_uow)

    product_id = uuid4()
    product = Product(
        id=product_id,
        name="Old",
        kind="Legacy",
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )
    fake_uow.products.get_by_id.return_value = product

    dto = await service.update_product(product_id, ProductUpdateDto(name="New"))

    fake_uow.commit.assert_awaited_once()
    assert dto.name == "New"


@pytest.mark.asyncio
async def test_products_service_update_product_not_found(
    fake_uow: FakeUnitOfWork,
) -> None:
    service = ProductsService(fake_uow)

    with pytest.raises(EntityNotFoundError):
        await service.update_product(uuid4(), ProductUpdateDto(name="New"))


@pytest.mark.asyncio
async def test_customers_service_update_customer(fake_uow: FakeUnitOfWork) -> None:
    service = CustomersService(fake_uow)

    customer_id = uuid4()
    customer = Customer(
        id=customer_id,
        name="Acme",
        email="acme@example.com",
        notifications_enabled=True,
        gem_fury_used=True,
        customer_symbol="ACM",
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )
    fake_uow.customers.get_by_id.return_value = customer

    dto = await service.update_customer(
        customer_id,
        payload=CustomerUpdateDto(name="Acme 2"),
    )

    assert dto.name == "Acme 2"
    fake_uow.commit.assert_awaited_once()
