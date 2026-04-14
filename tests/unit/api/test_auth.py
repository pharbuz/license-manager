from __future__ import annotations

from types import SimpleNamespace

from app.license_manager.api.helpers.auth import (
    ADMIN_ROLE,
    user_has_admin_role,
    user_has_any_app_role,
)


def test_user_has_admin_role_accepts_admin_role() -> None:
    user = SimpleNamespace(roles=[ADMIN_ROLE])

    assert user_has_admin_role(user)


def test_user_has_any_app_role_accepts_app_role() -> None:
    user = SimpleNamespace(roles=["app.viewer"])

    assert user_has_any_app_role(user)
