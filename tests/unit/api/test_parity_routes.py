from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.license_manager.api.dependencies import get_uow
from app.license_manager.api.v1.routers import (
    app_packages,
    customers,
    kinds,
    licenses,
    products,
)


def test_new_templates_exist() -> None:
    app = FastAPI()
    app.include_router(customers.router)
    app.include_router(kinds.router)
    app.include_router(products.router)

    client = TestClient(app)

    assert client.get("/customers/new").status_code == 200
    assert client.get("/kinds/new").status_code == 200
    assert client.get("/products/new").status_code == 200


def test_generate_license_key() -> None:
    app = FastAPI()
    app.include_router(licenses.router)
    client = TestClient(app)

    response = client.post(
        "/licenses/generate",
        json={
            "customerSymbol": "ACME",
            "endDate": "2026-12-31T00:00:00",
            "licenseCount": 5,
        },
    )

    assert response.status_code == 200
    assert response.json()["licenseKey"]


def test_app_package_download_and_notify(monkeypatch, tmp_path) -> None:
    binary = tmp_path / "agent.bin"
    binary.write_text("payload", encoding="utf-8")
    version_id = uuid4()

    monkeypatch.setattr(
        "app.license_manager.api.v1.routers.app_packages.get_settings",
        lambda: SimpleNamespace(APP_PACKAGES_DIR=str(tmp_path)),
    )

    async def _get_app_package(agent_id, *_args, **_kwargs):
        assert agent_id == version_id
        return None

    fake_service = SimpleNamespace(get_app_package=_get_app_package)
    monkeypatch.setattr(
        "app.license_manager.api.v1.routers.app_packages.AppPackagesService",
        lambda _uow: fake_service,
    )
    notified_payloads = []
    monkeypatch.setattr(
        "app.license_manager.api.v1.routers.app_packages."
        "enqueue_app_package_update_notification_job",
        lambda payload: notified_payloads.append(payload),
    )

    app = FastAPI()

    async def _override_get_uow():
        yield SimpleNamespace()

    app.dependency_overrides[get_uow] = _override_get_uow
    app.include_router(app_packages.router)
    client = TestClient(app)
    app_package_id = uuid4()

    download = client.get(
        f"/app-packages/{app_package_id}/download", params={"filePath": binary.name}
    )
    assert download.status_code == 200
    assert download.headers["content-disposition"].startswith("attachment;")

    notify = client.get(
        f"/app-packages/{app_package_id}/notify",
        params={"versionId": str(version_id)},
    )
    assert notify.status_code == 204
    assert len(notified_payloads) == 1
    assert notified_payloads[0].version_id == version_id
