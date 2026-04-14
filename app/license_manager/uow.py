from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession

from app.license_manager.repositories import (
    AppPackagesRepository,
    AuditLogsRepository,
    CustomersRepository,
    KindsRepository,
    LicensesRepository,
    ProductsRepository,
    SettingsRepository,
    SmtpCredentialRepository,
)


class UnitOfWork(AbstractAsyncContextManager["UnitOfWork"]):
    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
    ) -> None:
        self._session_factory = session_factory

        self.session: AsyncSession | None = None
        self.app_packages: AppPackagesRepository | None = None
        self.audit_logs: AuditLogsRepository | None = None
        self.customers: CustomersRepository | None = None
        self.kinds: KindsRepository | None = None
        self.licenses: LicensesRepository | None = None
        self.products: ProductsRepository | None = None
        self.settings: SettingsRepository | None = None
        self.smtp_credentials: SmtpCredentialRepository | None = None

    async def __aenter__(self) -> UnitOfWork:
        self.session = self._session_factory()
        self.app_packages = AppPackagesRepository(self.session)
        self.audit_logs = AuditLogsRepository(self.session)
        self.customers = CustomersRepository(self.session)
        self.kinds = KindsRepository(self.session)
        self.licenses = LicensesRepository(self.session)
        self.products = ProductsRepository(self.session)
        self.settings = SettingsRepository(self.session)
        self.smtp_credentials = SmtpCredentialRepository()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            if exc:
                await self.rollback()
        finally:
            if self.session:
                await self.session.close()
            self._clear_references()

    def _clear_references(self) -> None:
        self.session = None
        self.app_packages = None
        self.audit_logs = None
        self.customers = None
        self.kinds = None
        self.licenses = None
        self.products = None
        self.settings = None
        self.smtp_credentials = None

    async def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("UnitOfWork is not active; commit() called prematurely")
        await self.session.commit()

    async def rollback(self) -> None:
        if self.session is None:
            return
        await self.session.rollback()
