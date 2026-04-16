from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.license_manager.db.models import (
    AppPackage,
    Customer,
    Kind,
    License,
    Product,
    Setting,
)
from app.license_manager.repositories.app_packages import AppPackagesRepository
from app.license_manager.repositories.audit_logs import AuditLogsRepository
from app.license_manager.repositories.customers import CustomersRepository
from app.license_manager.repositories.kinds import KindsRepository
from app.license_manager.repositories.licenses import LicensesRepository
from app.license_manager.repositories.products import ProductsRepository
from app.license_manager.repositories.settings import SettingsRepository


@pytest.fixture
def mock_session() -> Mock:
    session = Mock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    session.add = Mock()
    session.add_all = Mock()
    return session


@pytest.mark.asyncio
async def test_customers_repository_get_by_symbol_executes_query(
    mock_session: Mock,
) -> None:
    customer = Customer(
        id=uuid4(),
        name="Acme",
        email="acme@example.com",
        notifications_enabled=True,
        gem_fury_used=True,
        customer_symbol="ACM",
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )
    result = Mock()
    result.scalars.return_value.first.return_value = customer
    mock_session.execute.return_value = result

    repository = CustomersRepository(session=mock_session)
    fetched = await repository.get_by_symbol("ACM")

    assert fetched is customer
    stmt = mock_session.execute.call_args.args[0]
    assert isinstance(stmt, Select)


@pytest.mark.asyncio
async def test_customers_repository_list_dropdown_items_returns_rows(
    mock_session: Mock,
) -> None:
    customer_id = uuid4()
    mock_session.execute.return_value = Mock(
        all=Mock(return_value=[(customer_id, "ACM", "Acme")])
    )

    repository = CustomersRepository(session=mock_session)
    rows = await repository.list_dropdown_items()

    assert rows == [(customer_id, "ACM", "Acme")]
    stmt = mock_session.execute.call_args.args[0]
    assert isinstance(stmt, Select)


@pytest.mark.asyncio
async def test_kinds_repository_get_by_name_executes_query(mock_session: Mock) -> None:
    kind = Kind(
        id=uuid4(),
        name="Trial",
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )
    result = Mock()
    result.scalars.return_value.first.return_value = kind
    mock_session.execute.return_value = result

    repository = KindsRepository(session=mock_session)
    fetched = await repository.get_by_name("Trial")

    assert fetched is kind


@pytest.mark.asyncio
async def test_kinds_repository_count_for_dashboard_returns_scalar(
    mock_session: Mock,
) -> None:
    mock_session.execute.return_value = Mock(scalar_one=Mock(return_value=4))

    repository = KindsRepository(session=mock_session)
    count = await repository.count_for_dashboard()

    assert count == 4


@pytest.mark.asyncio
async def test_products_repository_get_by_name_executes_query(
    mock_session: Mock,
) -> None:
    product = Product(
        id=uuid4(),
        name="LicenseManager",
        kind="Standard",
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )
    result = Mock()
    result.scalars.return_value.first.return_value = product
    mock_session.execute.return_value = result

    repository = ProductsRepository(session=mock_session)
    fetched = await repository.get_by_name("LicenseManager")

    assert fetched is product


@pytest.mark.asyncio
async def test_products_repository_list_dropdown_items_returns_rows(
    mock_session: Mock,
) -> None:
    product_id = uuid4()
    mock_session.execute.return_value = Mock(
        all=Mock(return_value=[(product_id, "Gateway")])
    )

    repository = ProductsRepository(session=mock_session)
    rows = await repository.list_dropdown_items()

    assert rows == [(product_id, "Gateway")]


@pytest.mark.asyncio
async def test_licenses_repository_list_by_customer_id_returns_rows(
    mock_session: Mock,
) -> None:
    customer_id = uuid4()
    license_entity = License(
        id=uuid4(),
        customer_id=customer_id,
        product_id=None,
        kind_id=None,
        license_count=10,
        license_state="active",
        license_key="abc",
        license_email="user@example.com",
        double_send=False,
        begin_date=datetime(2026, 1, 1, 0, 0, 0),
        end_date=datetime(2026, 12, 31, 0, 0, 0),
        notification_date=datetime(2026, 12, 1, 0, 0, 0),
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )
    result = Mock()
    result.scalars.return_value.all.return_value = [license_entity]
    mock_session.execute.return_value = result

    repository = LicensesRepository(session=mock_session)
    rows = await repository.list_by_customer_id(customer_id)

    assert rows == [license_entity]


@pytest.mark.asyncio
async def test_licenses_repository_count_active_for_dashboard_returns_scalar(
    mock_session: Mock,
) -> None:
    mock_session.execute.return_value = Mock(scalar_one=Mock(return_value=9))

    repository = LicensesRepository(session=mock_session)
    count = await repository.count_active_for_dashboard()

    assert count == 9


@pytest.mark.asyncio
async def test_app_packages_repository_get_by_version_number_executes_query(
    mock_session: Mock,
) -> None:
    app_package = AppPackage(
        id=uuid4(),
        version_number="1.0.0",
        binary_name="agent",
        gem_fury_url="https://gem.fury",
        binary_url="https://binary.example",
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=datetime(2026, 1, 1, 0, 0, 0),
    )
    result = Mock()
    result.scalars.return_value.first.return_value = app_package
    mock_session.execute.return_value = result

    repository = AppPackagesRepository(session=mock_session)
    fetched = await repository.get_by_version_number("1.0.0")

    assert fetched is app_package


@pytest.mark.asyncio
async def test_audit_logs_repository_latest_occurrence_returns_first_scalar(
    mock_session: Mock,
) -> None:
    occurred_at = datetime(2026, 1, 2, 0, 0, 0)
    mock_session.execute.return_value = Mock(
        scalars=Mock(return_value=Mock(first=Mock(return_value=occurred_at)))
    )

    repository = AuditLogsRepository(session=mock_session)
    latest = await repository.get_latest_occurred_at_for_dashboard()

    assert latest == occurred_at


@pytest.mark.asyncio
async def test_settings_repository_get_by_object_id_executes_query(
    mock_session: Mock,
) -> None:
    setting = Setting(
        schema_id="recommendations.ignores",
        scope="customer:acme",
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=None,
        created_by="system",
        modified_by=None,
        value={"enabled": True},
    )
    result = Mock()
    result.scalars.return_value.first.return_value = setting
    mock_session.execute.return_value = result

    repository = SettingsRepository(session=mock_session)
    fetched = await repository.get_by_object_id(setting.object_id)

    assert fetched is setting
    stmt = mock_session.execute.call_args.args[0]
    assert isinstance(stmt, Select)


@pytest.mark.asyncio
async def test_settings_repository_list_by_schema_and_scope_returns_rows(
    mock_session: Mock,
) -> None:
    setting = Setting(
        schema_id="recommendations.ignores",
        scope="customer:acme",
        created_at=datetime(2026, 1, 1, 0, 0, 0),
        modified_at=None,
        created_by="system",
        modified_by=None,
        value={"enabled": True},
    )
    result = Mock()
    result.scalars.return_value.all.return_value = [setting]
    mock_session.execute.return_value = result

    repository = SettingsRepository(session=mock_session)
    rows = await repository.list_by_schema_and_scope(
        schema_id="recommendations.ignores",
        scope="customer:acme",
    )

    assert rows == [setting]
