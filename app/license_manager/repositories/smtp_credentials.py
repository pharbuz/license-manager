from __future__ import annotations

import asyncio
import json
import re

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from app.license_manager.core.settings import get_settings
from app.license_manager.observability.logging import get_logger
from app.license_manager.services.models.smtp_credentials import (
    SmtpCredentialSecretPayload,
)

logger = get_logger(__name__)


def _sanitize_secret_name(name: str) -> str:
    safe = re.sub(r"[^0-9a-zA-Z-]", "-", name)
    safe = re.sub(r"-+", "-", safe).strip("-")
    return safe[:127] or "smtp-credentials"


class SmtpCredentialRepository:
    def __init__(
        self,
        *,
        vault_url: str | None = None,
        secret_name: str | None = None,
        client: SecretClient | None = None,
    ) -> None:
        settings = get_settings()
        self.vault_url = vault_url or settings.AZURE_KEY_VAULT_URL
        if not self.vault_url:
            raise RuntimeError("AZURE_KEY_VAULT_URL is not configured in settings.")

        self.secret_name = _sanitize_secret_name(
            secret_name or settings.SMTP_CREDENTIALS_SECRET_NAME
        )

        if client is not None:
            self.client = client
            return

        if (
            settings.AZURE_TENANT_ID
            and settings.AZURE_CLIENT_ID
            and settings.AZURE_CLIENT_SECRET
        ):
            credential: DefaultAzureCredential | ClientSecretCredential = (
                ClientSecretCredential(
                    tenant_id=settings.AZURE_TENANT_ID,
                    client_id=settings.AZURE_CLIENT_ID,
                    client_secret=settings.AZURE_CLIENT_SECRET,
                )
            )
        else:
            credential = DefaultAzureCredential(
                exclude_cli_credential=not settings.AZURE_USE_CLI_CREDENTIAL
            )

        self.client = SecretClient(vault_url=self.vault_url, credential=credential)

    async def exists(self) -> bool:
        try:
            await asyncio.to_thread(self.client.get_secret, self.secret_name)
            return True
        except ResourceNotFoundError:
            return False

    async def store(
        self, payload: SmtpCredentialSecretPayload
    ) -> tuple[str, str | None]:
        value = json.dumps(
            payload.model_dump(by_alias=True, mode="json"), separators=(",", ":")
        )
        logger.info(
            "Storing SMTP credential secret", extra={"secret_name": self.secret_name}
        )
        result = await asyncio.to_thread(
            self.client.set_secret,
            self.secret_name,
            value,
            content_type="application/json",
        )
        return result.name, getattr(result.properties, "version", None)

    async def fetch(self) -> tuple[str, str | None, SmtpCredentialSecretPayload]:
        logger.info(
            "Fetching SMTP credential secret", extra={"secret_name": self.secret_name}
        )
        try:
            result = await asyncio.to_thread(self.client.get_secret, self.secret_name)
        except ResourceNotFoundError as exc:
            raise exc

        payload = SmtpCredentialSecretPayload.model_validate(json.loads(result.value))
        return result.name, getattr(result.properties, "version", None), payload

    async def delete(self, *, purge: bool = True) -> None:
        logger.info(
            "Deleting SMTP credential secret",
            extra={"secret_name": self.secret_name, "purge": purge},
        )
        await asyncio.to_thread(self.client.begin_delete_secret, self.secret_name)
        if purge:
            await self.purge_deleted_secret()

    async def purge_deleted_secret(self) -> None:
        max_retries = 8
        base_delay = 0.25
        for attempt in range(max_retries):
            try:
                await asyncio.to_thread(
                    self.client.purge_deleted_secret, self.secret_name
                )
                return
            except HttpResponseError as exc:
                status = getattr(exc, "status_code", None)
                if status is None:
                    response = getattr(exc, "response", None)
                    status = (
                        getattr(response, "status_code", None) if response else None
                    )
                message = str(exc)
                is_conflict = int(status or 0) == 409 and (
                    "being deleted" in message or "currently being deleted" in message
                )
                if is_conflict and attempt < max_retries - 1:
                    await asyncio.sleep(min(base_delay * (2**attempt), 2.0))
                    continue
                raise
