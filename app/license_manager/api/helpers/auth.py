from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from fastapi import Depends, HTTPException, Request, status

ADMIN_ROLE = "app.admin"
DOCS_TOKEN_COOKIE_NAME = "docs_token"


def get_keycloak(request: Request) -> Any:
    keycloak = getattr(request.app.state, "keycloak", None)
    if keycloak is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return keycloak


async def get_current_user(request: Request):
    return await _get_current_user(request)


async def get_current_docs_user(request: Request):
    return await _get_current_user(request, allow_docs_cookie=True)


async def _get_current_user(
    request: Request,
    *,
    allow_docs_cookie: bool = False,
):
    user = getattr(request.state, "current_user", None)
    if user is not None:
        return user

    keycloak = get_keycloak(request)
    user_dependency = keycloak.get_current_user(extra_fields=["groups"])
    token = _get_bearer_token(request)
    if token is None and allow_docs_cookie:
        token = request.cookies.get(DOCS_TOKEN_COOKIE_NAME)
    if token is None:
        user_auth_scheme = getattr(keycloak, "user_auth_scheme", None)
        if user_auth_scheme is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        token = await user_auth_scheme(request)

    user = user_dependency(token)
    user.extra_fields["groups"] = _parse_groups(user.extra_fields.get("groups"))
    setattr(request.state, "current_user", user)  # noqa: B010
    return user


def _get_bearer_token(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization") or ""
    if not auth_header.lower().startswith("bearer "):
        return None
    token = auth_header[7:].strip()
    return token or None


def require_admin_role(user=Depends(get_current_user)):
    if not user_has_admin_role(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user


def require_docs_admin_role(user=Depends(get_current_docs_user)):
    if not user_has_admin_role(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user


def user_has_admin_role(user) -> bool:
    roles = getattr(user, "roles", None) or []
    if isinstance(roles, str):
        return roles == ADMIN_ROLE
    try:
        return ADMIN_ROLE in roles
    except TypeError:
        return False


def user_has_any_app_role(user) -> bool:
    roles = getattr(user, "roles", None) or []
    if isinstance(roles, str):
        return roles.startswith("app.")
    try:
        return any(role.startswith("app.") for role in roles)
    except TypeError:
        return False


def _normalize_group(group: object) -> str | None:
    if not isinstance(group, str):
        return None
    normalized = group.strip()
    if not normalized:
        return None
    if "/" in normalized:
        segments = [segment for segment in normalized.split("/") if segment]
        if not segments:
            return None
        normalized = segments[-1]
    return normalized


def _parse_groups(raw_groups: object) -> list[str]:
    if not raw_groups:
        return []

    if isinstance(raw_groups, str):
        candidate_groups: Iterable[str] = [raw_groups]
    else:
        try:
            candidate_groups = list(raw_groups)  # type: ignore[arg-type]
        except TypeError:
            return []

    seen: set[str] = set()
    parsed: list[str] = []
    for group in candidate_groups:
        normalized = _normalize_group(group)
        if normalized and normalized not in seen:
            seen.add(normalized)
            parsed.append(normalized)

    return parsed
