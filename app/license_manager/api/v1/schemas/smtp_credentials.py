from __future__ import annotations

from datetime import datetime

from pydantic import EmailStr, Field

from app.license_manager.api.v1.schemas.common import BaseCamelSchema


class SmtpCredentialSchema(BaseCamelSchema):
    secret_name: str
    secret_version: str | None = Field(default=None)
    host: str
    port: int
    username: str
    sender_email: EmailStr | None = Field(default=None)
    use_tls: bool = True
    use_ssl: bool = False
    created_at: datetime
    modified_at: datetime


class SmtpCredentialCreateSchema(BaseCamelSchema):
    host: str
    port: int
    username: str
    password: str
    sender_email: EmailStr | None = Field(default=None)
    use_tls: bool = True
    use_ssl: bool = False


class SmtpCredentialUpdateSchema(BaseCamelSchema):
    host: str | None = Field(default=None)
    port: int | None = Field(default=None)
    username: str | None = Field(default=None)
    password: str | None = Field(default=None)
    sender_email: EmailStr | None = Field(default=None)
    use_tls: bool | None = Field(default=None)
    use_ssl: bool | None = Field(default=None)
