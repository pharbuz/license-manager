from __future__ import annotations

from datetime import UTC, datetime

from azure.core.exceptions import ResourceNotFoundError

from app.license_manager.observability.logging import get_logger
from app.license_manager.repositories.smtp_credentials import SmtpCredentialRepository
from app.license_manager.services.errors import EntityNotFoundError
from app.license_manager.services.models.smtp_credentials import (
    SmtpCredentialCreateDto,
    SmtpCredentialDto,
    SmtpCredentialSecretPayload,
    SmtpCredentialUpdateDto,
)

logger = get_logger(__name__)


class SmtpCredentialService:
    def __init__(self, repository: SmtpCredentialRepository | None = None) -> None:
        self.repository = repository or SmtpCredentialRepository()

    @staticmethod
    def _to_output(
        secret_name: str,
        secret_version: str | None,
        payload: SmtpCredentialSecretPayload,
    ) -> SmtpCredentialDto:
        return SmtpCredentialDto(
            secret_name=secret_name,
            secret_version=secret_version,
            host=payload.host,
            port=payload.port,
            username=payload.username,
            sender_email=payload.sender_email,
            use_tls=payload.use_tls,
            use_ssl=payload.use_ssl,
            created_at=payload.created_at,
            modified_at=payload.modified_at,
        )

    async def get_smtp_credentials(self) -> SmtpCredentialDto:
        try:
            secret_name, secret_version, payload = await self.repository.fetch()
        except ResourceNotFoundError as exc:
            raise EntityNotFoundError("SMTP credentials not found") from exc
        return self._to_output(secret_name, secret_version, payload)

    async def create_smtp_credentials(
        self, payload: SmtpCredentialCreateDto
    ) -> SmtpCredentialDto:
        now = datetime.now(UTC)
        secret_payload = SmtpCredentialSecretPayload(
            host=payload.host,
            port=payload.port,
            username=payload.username,
            password=payload.password,
            sender_email=payload.sender_email,
            use_tls=payload.use_tls,
            use_ssl=payload.use_ssl,
            created_at=now,
            modified_at=now,
        )
        secret_name, secret_version = await self.repository.store(secret_payload)
        return self._to_output(secret_name, secret_version, secret_payload)

    async def update_smtp_credentials(
        self, payload: SmtpCredentialUpdateDto
    ) -> SmtpCredentialDto:
        try:
            secret_name, _, current = await self.repository.fetch()
        except ResourceNotFoundError as exc:
            raise EntityNotFoundError("SMTP credentials not found") from exc

        updated = SmtpCredentialSecretPayload(
            host=payload.host or current.host,
            port=payload.port or current.port,
            username=payload.username or current.username,
            password=payload.password or current.password,
            sender_email=(
                payload.sender_email
                if payload.sender_email is not None
                else current.sender_email
            ),
            use_tls=payload.use_tls if payload.use_tls is not None else current.use_tls,
            use_ssl=payload.use_ssl if payload.use_ssl is not None else current.use_ssl,
            created_at=current.created_at,
            modified_at=datetime.now(UTC),
        )
        _, secret_version = await self.repository.store(updated)
        return self._to_output(secret_name, secret_version, updated)

    async def delete_smtp_credentials(self, *, purge: bool = True) -> None:
        try:
            await self.repository.delete(purge=purge)
        except ResourceNotFoundError as exc:
            raise EntityNotFoundError("SMTP credentials not found") from exc
