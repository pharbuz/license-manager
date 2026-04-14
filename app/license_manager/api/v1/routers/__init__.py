from app.license_manager.api.v1.routers.app_packages import (
    router as app_packages_router,
)
from app.license_manager.api.v1.routers.audit_logs import router as audit_logs_router
from app.license_manager.api.v1.routers.customers import router as customers_router
from app.license_manager.api.v1.routers.kinds import router as kinds_router
from app.license_manager.api.v1.routers.licenses import router as licenses_router
from app.license_manager.api.v1.routers.products import router as products_router
from app.license_manager.api.v1.routers.smtp_credentials import (
    router as smtp_credentials_router,
)

__all__ = [
    "audit_logs_router",
    "customers_router",
    "kinds_router",
    "licenses_router",
    "products_router",
    "smtp_credentials_router",
    "app_packages_router",
]
