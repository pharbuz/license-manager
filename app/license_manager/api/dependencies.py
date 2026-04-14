from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Request

from app.license_manager.db import session as db_session
from app.license_manager.uow import UnitOfWork


async def get_uow(request: Request) -> AsyncIterator[UnitOfWork]:
    """FastAPI dependency that yields an active UnitOfWork per request."""
    if db_session.AsyncSessionLocal is None:
        db_session.get_engine()
    assert db_session.AsyncSessionLocal is not None

    uow = UnitOfWork(db_session.AsyncSessionLocal)
    async with uow as active_uow:
        yield active_uow
