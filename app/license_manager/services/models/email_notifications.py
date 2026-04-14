from __future__ import annotations

from app.license_manager.services.models.common import BaseCamelModel


class EmailAttachment(BaseCamelModel):
    filename: str
    content: bytes
    mime_type: str = "application/octet-stream"
