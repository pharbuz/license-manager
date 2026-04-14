from __future__ import annotations

from collections.abc import Iterable


def parse_list_setting(value: object) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.startswith("[") and text.endswith("]"):
            import json

            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in text.split(",") if item.strip()]
    if isinstance(value, Iterable):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else None


def build_notification_receivers(
    *,
    license_email: str,
    customer_email: str | None,
    double_send: bool,
) -> list[str]:
    if not customer_email or license_email == customer_email:
        return [license_email]
    if double_send:
        return [license_email, customer_email]
    return [license_email]


def build_contact_person_greeting(contact_person_name: str | None) -> str:
    if not contact_person_name:
        return "Hi there"
    return f"Dear {contact_person_name.split(' ')[0]}"


def parse_semantic_version(version: str) -> tuple[int, int, int]:
    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)
