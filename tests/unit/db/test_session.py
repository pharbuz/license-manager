from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.license_manager.db import session as session_module


def test_get_engine_uses_settings_dsn(monkeypatch) -> None:
    fake_engine = object()
    fake_factory = Mock(return_value="session-factory")
    captured: dict[str, object] = {}

    class Settings:
        POSTGRES_DSN = "postgresql+asyncpg://user:pass@db:5432/license_manager"
        POSTGRES_USER = None
        POSTGRES_PASSWORD = None
        POSTGRES_HOST = None
        POSTGRES_PORT = None
        POSTGRES_DB = None
        SQLALCHEMY_ECHO = True
        SQLALCHEMY_POOL_SIZE = 7
        SQLALCHEMY_MAX_OVERFLOW = 9
        SQLALCHEMY_POOL_PRE_PING = False
        SQLALCHEMY_POOL_RECYCLE = 123

    def fake_get_settings() -> Settings:
        return Settings()

    def fake_create_async_engine(database_url: str, **kwargs):
        captured["database_url"] = database_url
        captured.update(kwargs)
        return fake_engine

    monkeypatch.setattr(session_module, "_engine", None)
    monkeypatch.setattr(session_module, "AsyncSessionLocal", None)
    monkeypatch.setattr(session_module, "get_settings", fake_get_settings)
    monkeypatch.setattr(session_module, "create_async_engine", fake_create_async_engine)
    monkeypatch.setattr(session_module, "async_sessionmaker", fake_factory)

    engine = session_module.get_engine()

    assert engine is fake_engine
    assert captured["database_url"] == Settings.POSTGRES_DSN
    assert captured["echo"] is True
    assert captured["pool_size"] == 7
    assert captured["max_overflow"] == 9
    assert captured["pool_pre_ping"] is False
    assert captured["pool_recycle"] == 123
    assert session_module.AsyncSessionLocal is fake_factory.return_value


@pytest.mark.asyncio
async def test_init_db_creates_declared_schemas_before_tables(monkeypatch) -> None:
    create_all = Mock()
    fake_metadata = SimpleNamespace(
        tables={
            "app_packages": SimpleNamespace(schema="licensemanager"),
            "settings": SimpleNamespace(schema="licensemanager"),
            "temporary": SimpleNamespace(schema=None),
        },
        create_all=create_all,
    )
    events: list[tuple[str, object]] = []

    async def fake_execute(statement: object) -> None:
        events.append(("execute", statement))

    async def fake_run_sync(callback: object) -> None:
        events.append(("run_sync", callback))

    class FakeBegin:
        async def __aenter__(self) -> SimpleNamespace:
            return SimpleNamespace(execute=fake_execute, run_sync=fake_run_sync)

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

    fake_engine = SimpleNamespace(begin=lambda: FakeBegin())

    monkeypatch.setattr(session_module, "get_engine", lambda: fake_engine)
    monkeypatch.setattr(session_module.Base, "metadata", fake_metadata, raising=False)

    await session_module.init_db()

    assert len(events) == 2
    assert events[0][0] == "execute"
    assert str(events[0][1]) == "CREATE SCHEMA IF NOT EXISTS licensemanager"
    assert events[1] == ("run_sync", create_all)
