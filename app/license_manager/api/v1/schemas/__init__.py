from app.license_manager.api.v1.schemas.app_packages import (
    AppPackageCreateSchema,
    AppPackageDownloadQuerySchema,
    AppPackageNotifyQuerySchema,
    AppPackageSchema,
    AppPackageUpdateSchema,
)
from app.license_manager.api.v1.schemas.audit_logs import (
    AuditLogEntrySchema,
    AuditLogQueryParams,
)
from app.license_manager.api.v1.schemas.customers import (
    CustomerCreateSchema,
    CustomerSchema,
    CustomerUpdateSchema,
)
from app.license_manager.api.v1.schemas.health import HealthOut, HealthServicesOut
from app.license_manager.api.v1.schemas.kinds import (
    KindCreateSchema,
    KindSchema,
    KindUpdateSchema,
)
from app.license_manager.api.v1.schemas.licenses import (
    LicenseCreateSchema,
    LicenseGeneratedKeySchema,
    LicenseGenerateQuerySchema,
    LicenseSchema,
    LicenseUpdateSchema,
)
from app.license_manager.api.v1.schemas.products import (
    ProductCreateSchema,
    ProductSchema,
    ProductUpdateSchema,
)
from app.license_manager.api.v1.schemas.smtp_credentials import (
    SmtpCredentialCreateSchema,
    SmtpCredentialSchema,
    SmtpCredentialUpdateSchema,
)

__all__ = [
    "AuditLogEntrySchema",
    "AuditLogQueryParams",
    "CustomerSchema",
    "CustomerCreateSchema",
    "CustomerUpdateSchema",
    "HealthOut",
    "HealthServicesOut",
    "KindSchema",
    "KindCreateSchema",
    "KindUpdateSchema",
    "ProductSchema",
    "ProductCreateSchema",
    "ProductUpdateSchema",
    "SmtpCredentialSchema",
    "SmtpCredentialCreateSchema",
    "SmtpCredentialUpdateSchema",
    "LicenseSchema",
    "LicenseCreateSchema",
    "LicenseUpdateSchema",
    "LicenseGenerateQuerySchema",
    "LicenseGeneratedKeySchema",
    "AppPackageSchema",
    "AppPackageCreateSchema",
    "AppPackageUpdateSchema",
    "AppPackageDownloadQuerySchema",
    "AppPackageNotifyQuerySchema",
]
