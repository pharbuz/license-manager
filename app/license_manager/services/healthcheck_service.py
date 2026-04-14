from __future__ import annotations

from asyncio import gather, to_thread

from fastapi import FastAPI
from sqlalchemy import text

from app.license_manager.core.settings import get_settings
from app.license_manager.db.session import get_engine
from app.license_manager.observability.logging import get_logger
from app.license_manager.repositories.smtp_credentials import SmtpCredentialRepository
from app.license_manager.services.models.healthcheck import (
    HealthCheckModel,
    HealthOverallStatus,
    HealthServicesModel,
    HealthServiceStatus,
)

logger = get_logger(__name__)


class HealthCheckService:
    def __init__(self, app: FastAPI) -> None:
        self.app = app
        self.settings = get_settings()

    async def get_health(self) -> HealthCheckModel:
        postgres_result, key_vault_result = await gather(
            self._check_postgres_health(),
            self._check_key_vault_health(),
        )

        checks = {
            "postgres": postgres_result,
            "keyVault": key_vault_result,
        }

        errors = {
            name: result[1]
            for name, result in checks.items()
            if not result[0] and result[1]
        }

        services = HealthServicesModel(
            postgres=(
                HealthServiceStatus.OK
                if checks["postgres"][0]
                else HealthServiceStatus.ERROR
            ),
            key_vault=(
                HealthServiceStatus.OK
                if checks["keyVault"][0]
                else HealthServiceStatus.ERROR
            ),
        )

        status = (
            HealthOverallStatus.OK
            if all(result[0] for result in checks.values())
            else HealthOverallStatus.DEGRADED
        )

        return HealthCheckModel(status=status, services=services, errors=errors)

    async def _check_postgres_health(self) -> tuple[bool, str | None]:
        try:
            engine = get_engine()
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True, None
        except Exception as exc:
            logger.warning("PostgreSQL health check failed: %s", exc)
            return False, str(exc)

    async def _check_key_vault_health(self) -> tuple[bool, str | None]:
        if not self.settings.AZURE_KEY_VAULT_URL:
            return False, "AZURE_KEY_VAULT_URL is not configured"

        try:
            repository = SmtpCredentialRepository()
            probe_secret_name = "__license-manager-healthcheck-probe__"
            await to_thread(repository.client.get_secret, probe_secret_name)
            return True, None
        except Exception as exc:
            message = str(exc)
            if "(SecretNotFound)" in message:
                return True, None
            logger.warning("Azure Key Vault health check failed: %s", exc)
            return False, message
