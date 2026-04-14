from __future__ import annotations

import app.license_manager.db.session as db_session
from app.license_manager.uow import UnitOfWork


def new_uow() -> UnitOfWork:
    db_session.get_engine()
    if db_session.AsyncSessionLocal is None:
        raise RuntimeError("AsyncSessionLocal is not initialized")
    return UnitOfWork(db_session.AsyncSessionLocal)
