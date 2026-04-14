from __future__ import annotations

import importlib.util
import logging
import logging.config
from pathlib import Path
from typing import Any

from app.license_manager.core.settings import get_settings


class RequestIDLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        request_id = getattr(record, "request_id", None)
        record.request_id = request_id or "-"
        return True


def _json_formatter_installed() -> bool:
    return importlib.util.find_spec("pythonjsonlogger") is not None


def build_logging_config(level: str | int | None = None) -> dict[str, Any]:
    settings = get_settings()
    effective_level = level if level is not None else settings.LOG_LEVEL
    if isinstance(effective_level, str):
        effective_level = effective_level.upper()

    json_available = _json_formatter_installed()
    use_json = settings.LOG_JSON and json_available

    formatters: dict[str, Any] = {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s [request_id=%(request_id)s]",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    }
    if use_json:
        formatters["json"] = {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
        }

    filters: dict[str, Any] = {
        "request_id": {
            "()": "app.license_manager.observability.logging.RequestIDLogFilter",
        }
    }

    handlers: dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json" if use_json else "default",
            "level": effective_level,
            "stream": "ext://sys.stdout",
            "filters": ["request_id"],
        }
    }

    if settings.LOG_TO_FILE and settings.LOG_FILE:
        handlers["app_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.LOG_FILE,
            "maxBytes": settings.LOG_FILE_MAX_BYTES,
            "backupCount": settings.LOG_FILE_BACKUP_COUNT,
            "encoding": "utf-8",
            "formatter": "json" if use_json else "default",
            "level": effective_level,
            "filters": ["request_id"],
        }
    if settings.LOG_ERROR_FILE:
        handlers["error_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.LOG_ERROR_FILE,
            "maxBytes": settings.LOG_FILE_MAX_BYTES,
            "backupCount": settings.LOG_FILE_BACKUP_COUNT,
            "encoding": "utf-8",
            "formatter": "json" if use_json else "default",
            "level": "ERROR",
            "filters": ["request_id"],
        }

    active_handlers = [
        h for h in ("console", "app_file", "error_file") if h in handlers
    ]

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": filters,
        "formatters": formatters,
        "handlers": handlers,
        "root": {"handlers": active_handlers, "level": effective_level},
        "loggers": {
            "uvicorn": {
                "handlers": active_handlers,
                "level": effective_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": active_handlers,
                "level": effective_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": active_handlers,
                "level": effective_level,
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": active_handlers,
                "level": "WARNING",
                "propagate": False,
            },
        },
    }


def _ensure_log_file_directories(logging_config: dict[str, Any]) -> None:
    handlers: dict[str, Any] = logging_config.get("handlers", {})
    for handler in handlers.values():
        if "RotatingFileHandler" not in str(handler.get("class", "")):
            continue

        filename = handler.get("filename")
        if not filename:
            continue

        Path(filename).parent.mkdir(parents=True, exist_ok=True)


def setup_logging(level: str | int | None = None) -> None:
    config = build_logging_config(level)
    _ensure_log_file_directories(config)
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
