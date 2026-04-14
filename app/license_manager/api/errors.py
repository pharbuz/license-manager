from __future__ import annotations

import datetime as _dt
from typing import Any
from uuid import UUID

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.license_manager.api.v1.schemas.common import RFC7807Error
from app.license_manager.observability.logging import get_logger
from app.license_manager.services.errors import EntityNotFoundError

logger = get_logger(__name__)

DEFAULT_PROBLEM_TYPE = "about:blank"
RFC_9457_TYPE = "https://datatracker.ietf.org/doc/html/rfc9457"
UNPROCESSABLE_ENTITY_TITLE = "Unprocessable Entity"


def _json_safe(obj: Any) -> Any:
    if obj is None or isinstance(obj, str | int | float | bool):
        return obj
    if isinstance(obj, _dt.datetime | _dt.date | _dt.time):
        try:
            return obj.isoformat()
        except Exception:
            return str(obj)
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple | set):
        return [_json_safe(v) for v in obj]
    try:
        from pydantic import BaseModel

        if isinstance(obj, BaseModel):
            try:
                return obj.model_dump()
            except Exception:
                pass
    except Exception:
        pass
    return repr(obj)[:1000]


def _problem_json(
    *,
    request: Request,
    status_code: int,
    title: str,
    detail: Any | None = None,
    type_: str = DEFAULT_PROBLEM_TYPE,
) -> JSONResponse:
    problem = RFC7807Error(
        type=type_,
        title=title,
        status=status_code,
        detail=_json_safe(detail),
        instance=str(request.url),
        request_id=getattr(request.state, "request_id", None),
    )
    content = _json_safe(problem.model_dump(by_alias=True))
    return JSONResponse(
        status_code=status_code,
        content=content,
        media_type="application/problem+json",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the API."""

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        logger.debug("HTTP exception: %s", exc)
        title = exc.detail if isinstance(exc.detail, str) else "HTTP error"
        detail = None if isinstance(exc.detail, str) else exc.detail
        return _problem_json(
            request=request,
            status_code=exc.status_code,
            title=title,
            detail=detail,
            type_=RFC_9457_TYPE,
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.debug("Request validation error: %s", exc)
        return _problem_json(
            request=request,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title=UNPROCESSABLE_ENTITY_TITLE,
            detail=exc.errors(),
            type_=RFC_9457_TYPE,
        )

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(
        request: Request, exc: EntityNotFoundError
    ) -> JSONResponse:
        logger.debug("Entity not found: %s", exc)
        return _problem_json(
            request=request,
            status_code=status.HTTP_404_NOT_FOUND,
            title="Entity not found",
            detail=str(exc),
            type_=RFC_9457_TYPE,
        )

    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(
        request: Request, exc: RuntimeError
    ) -> JSONResponse:
        logger.exception("Runtime error: %s", exc)
        return _problem_json(
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Internal Server Error",
            detail=str(exc),
            type_=RFC_9457_TYPE,
        )
