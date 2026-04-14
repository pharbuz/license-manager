from __future__ import annotations

from pathlib import Path
from typing import Any

from app.license_manager.observability.logging import setup_logging


class _Settings:
    LOG_LEVEL = "INFO"
    LOG_JSON = False
    LOG_TO_FILE = False
    LOG_FILE: str | None = None
    LOG_ERROR_FILE: str
    LOG_FILE_MAX_BYTES = 1024
    LOG_FILE_BACKUP_COUNT = 1

    def __init__(self, log_error_file: str) -> None:
        self.LOG_ERROR_FILE = log_error_file


def test_setup_logging_creates_log_directories_for_file_handlers(
    monkeypatch: Any, tmp_path: Path
) -> None:
    log_error_file = tmp_path / "logs" / "app.error.log"

    monkeypatch.setattr(
        "app.license_manager.observability.logging.get_settings",
        lambda: _Settings(str(log_error_file)),
    )

    captured: dict[str, Any] = {}

    def _fake_dict_config(config: dict[str, Any]) -> None:
        captured["config"] = config

    monkeypatch.setattr(
        "app.license_manager.observability.logging.logging.config.dictConfig",
        _fake_dict_config,
    )

    setup_logging()

    assert log_error_file.parent.exists()
    assert "config" in captured
