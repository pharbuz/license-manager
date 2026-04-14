from __future__ import annotations

from fastapi import APIRouter, Response, status

from app.license_manager.api.v1.schemas.smtp_credentials import (
    SmtpCredentialCreateSchema,
    SmtpCredentialSchema,
    SmtpCredentialUpdateSchema,
)
from app.license_manager.services.models.smtp_credentials import (
    SmtpCredentialCreateDto,
    SmtpCredentialUpdateDto,
)
from app.license_manager.services.smtp_credentials_service import SmtpCredentialService

router = APIRouter(prefix="/smtp-credentials", tags=["SMTP Credentials"])


def _to_schema(result: object) -> SmtpCredentialSchema:
    return SmtpCredentialSchema.model_validate(result, from_attributes=True)


@router.get("", response_model=SmtpCredentialSchema)
async def get_smtp_credentials() -> SmtpCredentialSchema:
    service = SmtpCredentialService()
    result = await service.get_smtp_credentials()
    return _to_schema(result)


@router.post(
    "", response_model=SmtpCredentialSchema, status_code=status.HTTP_201_CREATED
)
async def create_smtp_credentials(
    payload: SmtpCredentialCreateSchema,
) -> SmtpCredentialSchema:
    service = SmtpCredentialService()
    result = await service.create_smtp_credentials(
        SmtpCredentialCreateDto.model_validate(payload.model_dump())
    )
    return _to_schema(result)


@router.put("", response_model=SmtpCredentialSchema)
async def update_smtp_credentials(
    payload: SmtpCredentialUpdateSchema,
) -> SmtpCredentialSchema:
    service = SmtpCredentialService()
    result = await service.update_smtp_credentials(
        SmtpCredentialUpdateDto.model_validate(payload.model_dump())
    )
    return _to_schema(result)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_smtp_credentials() -> Response:
    service = SmtpCredentialService()
    await service.delete_smtp_credentials()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
