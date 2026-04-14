from __future__ import annotations

from sqlalchemy import UniqueConstraint

from app.license_manager.db.models import AppPackage, Customer, Kind, License, Product


def _has_unique_constraint(table, expected_name: str) -> bool:
    return any(
        isinstance(constraint, UniqueConstraint) and constraint.name == expected_name
        for constraint in table.constraints
    )


def test_customer_mapping_matches_dotnet() -> None:
    table = Customer.__table__

    assert table.schema == "licensemanager"
    assert table.name == "customers"
    assert _has_unique_constraint(table, "customersymbol_unique")
    assert table.c.customer_symbol.type.length == 3
    assert table.c.name.type.length == 128
    assert table.c.email.type.length == 128
    assert table.c.notifications_enabled.server_default is not None
    assert table.c.gem_fury_used.server_default is not None


def test_license_mapping_matches_dotnet() -> None:
    table = License.__table__

    assert table.schema == "licensemanager"
    assert table.name == "licenses"
    assert _has_unique_constraint(table, "licensekey_unique")
    assert table.c.license_key.type.length == 512
    assert table.c.license_state.type.length == 128

    customer_fk = next(iter(table.c.customer_id.foreign_keys))
    product_fk = next(iter(table.c.product_id.foreign_keys))
    kind_fk = next(iter(table.c.kind_id.foreign_keys))

    assert customer_fk.ondelete == "SET NULL"
    assert product_fk.ondelete == "SET NULL"
    assert kind_fk.ondelete == "SET NULL"


def test_other_models_mapping_matches_dotnet() -> None:
    kinds_table = Kind.__table__
    products_table = Product.__table__
    app_packages_table = AppPackage.__table__

    assert kinds_table.schema == "licensemanager"
    assert kinds_table.name == "kinds"
    assert kinds_table.c.name.type.length == 128

    assert products_table.schema == "licensemanager"
    assert products_table.name == "products"
    assert products_table.c.name.type.length == 128

    assert app_packages_table.schema == "licensemanager"
    assert app_packages_table.name == "app_packages"
    assert _has_unique_constraint(app_packages_table, "versionnumber_unique")
    assert app_packages_table.c.version_number.type.length == 16
