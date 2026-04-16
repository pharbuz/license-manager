from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.license_manager.api.errors import register_exception_handlers
from app.license_manager.services.errors import EntityNotFoundError


def _client() -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    return TestClient(app, raise_server_exceptions=False)


def test_entity_not_found_uses_problem_json() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/missing")
    async def missing() -> None:
        raise EntityNotFoundError("Customer 123 not found")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/missing")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["type"] == "https://datatracker.ietf.org/doc/html/rfc9457"
    assert response.json()["status"] == 404
    assert response.json()["instance"].endswith("/missing")
    assert response.json()["title"] == "Entity not found"
    assert response.json()["detail"] == "Customer 123 not found"


def test_runtime_error_uses_problem_json() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("UnitOfWork session is not initialized")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/boom")

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["type"] == "https://datatracker.ietf.org/doc/html/rfc9457"
    assert response.json()["title"] == "Internal Server Error"


def test_unhandled_exception_uses_problem_json() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/value-error")
    async def value_error() -> None:
        raise ValueError("unexpected dashboard failure")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/value-error")

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["type"] == "https://datatracker.ietf.org/doc/html/rfc9457"
    assert response.json()["title"] == "Internal Server Error"
    assert response.json()["detail"] == "unexpected dashboard failure"


def test_exception_group_uses_problem_json() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/exception-group")
    async def exception_group() -> None:
        raise ExceptionGroup("dashboard failed", [ValueError("inner failure")])

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/exception-group")

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["type"] == "https://datatracker.ietf.org/doc/html/rfc9457"
    assert response.json()["title"] == "Internal Server Error"
    assert response.json()["detail"] == "dashboard failed (1 sub-exception)"
