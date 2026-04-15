from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.schema import CreateSchema

from app.license_manager.core.settings import get_settings
from app.license_manager.db.base import Base

_engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def _get_declared_schemas() -> tuple[str, ...]:
    return tuple(
        sorted(
            {table.schema for table in Base.metadata.tables.values() if table.schema}
        )
    )


def get_engine() -> AsyncEngine:
    """Create or return a singleton AsyncEngine and session factory."""
    global _engine, AsyncSessionLocal
    if _engine is None:
        settings = get_settings()
        database_url = settings.POSTGRES_DSN or (
            f"postgresql+asyncpg://{settings.POSTGRES_USER or 'postgres'}"
            f":{settings.POSTGRES_PASSWORD or 'postgres'}"
            f"@{settings.POSTGRES_HOST or 'localhost'}:{settings.POSTGRES_PORT or 5432}"
            f"/{settings.POSTGRES_DB or 'license_manager'}"
        )
        _engine = create_async_engine(
            database_url,
            echo=settings.SQLALCHEMY_ECHO,
            pool_size=settings.SQLALCHEMY_POOL_SIZE,
            max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
            pool_pre_ping=settings.SQLALCHEMY_POOL_PRE_PING,
            pool_recycle=settings.SQLALCHEMY_POOL_RECYCLE,
        )
        AsyncSessionLocal = async_sessionmaker(
            _engine, expire_on_commit=False, class_=AsyncSession
        )
    return _engine


async def init_db() -> None:
    """Initialize DB access.

    Creates all tables based on SQLModel metadata if they don't exist.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        for schema_name in _get_declared_schemas():
            await conn.execute(CreateSchema(schema_name, if_not_exists=True))
        await conn.run_sync(Base.metadata.create_all)
