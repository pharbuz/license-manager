from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.license_manager.core.helpers import parse_list_setting


class Settings(BaseSettings):
    APP_NAME: str = "License Manager API"
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    KEYCLOAK_BASE_URL: str = Field(default="http://localhost:8080")
    KEYCLOAK_REALM: str = Field(default="master")
    KEYCLOAK_VERIFY_SSL: bool = Field(default=True)
    KEYCLOAK_CLIENT_ID: str = Field(default="license-manager")
    KEYCLOAK_CLIENT_SECRET: str = Field(default="")
    KEYCLOAK_ADMIN_SECRET: str = Field(default="")
    KEYCLOAK_CALLBACK_URI: str = Field(
        default="http://localhost:8000/docs/oauth2-redirect.html"
    )

    CORS_ALLOWED_ORIGINS: str | list[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOWED_METHODS: str | list[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOWED_HEADERS: str | list[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_CREDENTIALS: bool = True

    LOG_LEVEL: str = Field(default="INFO")
    LOG_JSON: bool = Field(default=True)
    LOG_TO_FILE: bool = Field(default=False)
    LOG_FILE: str | None = Field(default="logs/app.log")
    LOG_ERROR_FILE: str | None = Field(default="logs/app.error.log")
    LOG_FILE_MAX_BYTES: int = Field(default=10 * 1024 * 1024)
    LOG_FILE_BACKUP_COUNT: int = Field(default=5)

    AZURE_KEY_VAULT_URL: str | None = Field(default=None)
    AZURE_TENANT_ID: str | None = Field(default=None)
    AZURE_CLIENT_ID: str | None = Field(default=None)
    AZURE_CLIENT_SECRET: str | None = Field(default=None)
    AZURE_USE_CLI_CREDENTIAL: bool = Field(default=False)
    SMTP_CREDENTIALS_SECRET_NAME: str = Field(default="smtp-credentials")
    APP_PACKAGES_DIR: str = Field(default="AppPackages")

    POSTGRES_DSN: str | None = Field(
        default=None,
        validation_alias=AliasChoices("POSTGRES_DSN", "DATABASE_URL", "DB_DSN"),
    )
    POSTGRES_HOST: str | None = Field(default=None)
    POSTGRES_PORT: int | None = Field(default=None)
    POSTGRES_DB: str | None = Field(default=None)
    POSTGRES_USER: str | None = Field(default=None)
    POSTGRES_PASSWORD: str | None = Field(default=None)
    SQLALCHEMY_ECHO: bool = Field(default=False)
    SQLALCHEMY_POOL_SIZE: int = Field(default=5)
    SQLALCHEMY_MAX_OVERFLOW: int = Field(default=10)
    SQLALCHEMY_POOL_PRE_PING: bool = Field(default=True)
    SQLALCHEMY_POOL_RECYCLE: int | None = Field(default=None)

    CELERY_BROKER_URL: str | None = Field(default=None)
    CELERY_RESULT_BACKEND: str | None = Field(default=None)
    CELERY_TASK_DEFAULT_QUEUE: str = Field(default="license_manager")

    LICENSE_CHECK_CRON: str | None = Field(default=None)
    LICENSE_ARCHIVER_CRON: str | None = Field(default=None)
    LICENSE_CHECK_DAYS_FROM_TODAY_TO_CHECK: str | list[int] = Field(
        default_factory=lambda: [30, 14, 3]
    )

    @field_validator(
        "CORS_ALLOWED_ORIGINS",
        "CORS_ALLOWED_METHODS",
        "CORS_ALLOWED_HEADERS",
        mode="before",
    )
    @classmethod
    def _parse_list_fields(cls, value: Any) -> list[str]:
        parsed = parse_list_setting(value)
        return parsed or ["*"]

    @field_validator("LICENSE_CHECK_DAYS_FROM_TODAY_TO_CHECK", mode="before")
    @classmethod
    def _parse_days_to_check(cls, value: Any) -> list[int]:
        if isinstance(value, list):
            parsed = value
        else:
            parsed = parse_list_setting(value)

        if not parsed:
            return []

        days: list[int] = []
        for item in parsed:
            day = int(item)
            if day <= 0:
                raise ValueError(
                    "LICENSE_CHECK_DAYS_FROM_TODAY_TO_CHECK must contain only positive integers"
                )
            days.append(day)
        return days

    model_config = SettingsConfigDict(
        env_file="settings.dev.env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
