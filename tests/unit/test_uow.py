from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.license_manager.uow import UnitOfWork


@pytest.mark.asyncio
async def test_commit_raises_without_active_session() -> None:
    uow = UnitOfWork(session_factory=lambda: SimpleNamespace())

    with pytest.raises(RuntimeError, match="UnitOfWork is not active"):
        await uow.commit()


@pytest.mark.asyncio
async def test_rollback_calls_session_when_present() -> None:
    session = SimpleNamespace(rollback=AsyncMock())
    uow = UnitOfWork(session_factory=lambda: session)
    uow.session = session

    await uow.rollback()

    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_context_manager_builds_and_clears_repositories(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    smtp_repo = SimpleNamespace(fetch=AsyncMock())
    monkeypatch.setattr(
        "app.license_manager.uow.SmtpCredentialRepository",
        lambda: smtp_repo,
    )

    session = SimpleNamespace(
        close=AsyncMock(),
        rollback=AsyncMock(),
        commit=AsyncMock(),
    )
    uow = UnitOfWork(session_factory=lambda: session)

    async with uow as active_uow:
        assert active_uow.session is session
        assert active_uow.audit_logs is not None
        assert active_uow.customers is not None
        assert active_uow.kinds is not None
        assert active_uow.licenses is not None
        assert active_uow.products is not None
        assert active_uow.app_packages is not None
        assert active_uow.settings is not None
        assert active_uow.smtp_credentials is smtp_repo

    session.close.assert_awaited_once()
    assert uow.session is None
    assert uow.audit_logs is None
    assert uow.customers is None
    assert uow.kinds is None
    assert uow.licenses is None
    assert uow.products is None
    assert uow.app_packages is None
    assert uow.settings is None
    assert uow.smtp_credentials is None
