from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi_keycloak import FastAPIKeycloak

from app.license_manager.api.errors import register_exception_handlers
from app.license_manager.api.helpers.auth import (
    DOCS_TOKEN_COOKIE_NAME,
    require_docs_admin_role,
)
from app.license_manager.api.v1.routers import (
    app_packages_router,
    audit_logs_router,
    customers_router,
    dashboard_router,
    dropdown_router,
    kinds_router,
    licenses_router,
    products_router,
    smtp_credentials_router,
)
from app.license_manager.api.v1.schemas.health import HealthOut
from app.license_manager.core.settings import get_settings
from app.license_manager.db.session import init_db
from app.license_manager.middleware.problem_details import ProblemDetailsMiddleware
from app.license_manager.middleware.request_id import RequestIDMiddleware
from app.license_manager.middleware.timing import TimingMiddleware
from app.license_manager.observability.logging import get_logger, setup_logging
from app.license_manager.services.healthcheck_service import HealthCheckService
from app.license_manager.services.models.healthcheck import HealthOverallStatus

logger = get_logger(__name__)

TAGS_METADATA = [
    {
        "name": "Customers",
        "description": "Operations related to customers.",
    },
    {
        "name": "Kinds",
        "description": "Operations related to kinds.",
    },
    {
        "name": "Products",
        "description": "Operations related to products.",
    },
    {
        "name": "Licenses",
        "description": "Operations related to licenses.",
    },
    {
        "name": "AppPackages",
        "description": "Operations related to app packages.",
    },
    {
        "name": "SMTP Credentials",
        "description": "Operations related to SMTP credentials stored in Azure Key Vault.",
    },
    {
        "name": "AuditLogs",
        "description": "Audit trail of write operations.",
    },
    {
        "name": "Dropdown",
        "description": "Dropdown data sources for frontend form selectors.",
    },
    {
        "name": "Dashboard",
        "description": "Aggregated operational metrics for the dashboard view.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application lifecycle events."""
    setup_logging()
    logger.info("Logging configured.")
    await init_db()
    logger.info("Database initialized.")
    yield


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        description="API for managing licenses, customers, products, and app packages",
        version=settings.VERSION,
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
        openapi_tags=TAGS_METADATA,
        lifespan=lifespan,
    )

    idp: FastAPIKeycloak | None = None
    try:
        idp = FastAPIKeycloak(
            server_url=settings.KEYCLOAK_BASE_URL,
            client_id=settings.KEYCLOAK_CLIENT_ID,
            client_secret=settings.KEYCLOAK_CLIENT_SECRET,
            admin_client_secret=settings.KEYCLOAK_ADMIN_SECRET,
            realm=settings.KEYCLOAK_REALM,
            callback_uri=settings.KEYCLOAK_CALLBACK_URI,
            ssl_verification=settings.KEYCLOAK_VERIFY_SSL,
        )
        idp.add_swagger_config(app)
    except Exception as exc:
        logger.exception("Failed to initialize Keycloak client: %s", exc)

    issuer = (
        settings.KEYCLOAK_BASE_URL.rstrip("/") + f"/realms/{settings.KEYCLOAK_REALM}"
    )
    auth_url = issuer + "/protocol/openid-connect/auth"
    token_url = issuer + "/protocol/openid-connect/token"

    def custom_openapi() -> dict[str, object]:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        schema["tags"] = TAGS_METADATA
        schema.setdefault("components", {}).setdefault("securitySchemes", {})
        schema["components"]["securitySchemes"]["OAuth2"] = {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": auth_url,
                    "tokenUrl": token_url,
                    "scopes": {
                        "openid": "OpenID Connect",
                        "profile": "User profile",
                        "email": "User email",
                    },
                }
            },
        }
        schema["security"] = [{"OAuth2": ["openid", "profile", "email"]}]
        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOWED_METHODS,
        allow_headers=settings.CORS_ALLOWED_HEADERS,
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(ProblemDetailsMiddleware)
    app.add_middleware(TimingMiddleware)

    # Register exception handlers
    register_exception_handlers(app)

    # Include routers
    app.include_router(audit_logs_router)
    app.include_router(customers_router)
    app.include_router(dashboard_router)
    app.include_router(dropdown_router)
    app.include_router(kinds_router)
    app.include_router(licenses_router)
    app.include_router(products_router)
    app.include_router(smtp_credentials_router)
    app.include_router(app_packages_router)

    @app.get(
        "/openapi.json",
        include_in_schema=False,
        dependencies=[Depends(require_docs_admin_role)],
    )
    async def openapi_spec() -> JSONResponse:
        return JSONResponse(app.openapi())

    @app.get(
        "/docs/swagger",
        include_in_schema=False,
        response_class=HTMLResponse,
    )
    async def swagger_ui(request: Request) -> Response:
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer ") :]
        else:
            token = request.cookies.get(DOCS_TOKEN_COOKIE_NAME)
        if not token:
            redirect = RedirectResponse(url="/docs/login")
            redirect.status_code = 302
            return redirect
        if idp is None:
            return HTMLResponse(
                content="Documentation authentication is not configured.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        try:
            idp.get_current_user()(token=token)
        except HTTPException:
            resp = RedirectResponse(url="/docs/swagger", status_code=302)
            resp.delete_cookie(DOCS_TOKEN_COOKIE_NAME)
            return resp
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="License Manager API - Swagger",
            oauth2_redirect_url="/docs/oauth2-redirect.html",
            swagger_ui_parameters={"persistAuthorization": True},
            init_oauth={
                "clientId": settings.KEYCLOAK_CLIENT_ID,
                "scopes": "openid profile email",
                "usePkceWithAuthorizationCodeGrant": True,
            },
        )

    @app.get(
        "/docs/redoc",
        include_in_schema=False,
        dependencies=[Depends(require_docs_admin_role)],
    )
    async def redoc_ui() -> Response:
        return get_redoc_html(
            openapi_url="/openapi.json", title="License Manager API - ReDoc"
        )

    @app.get("/docs/login", include_in_schema=False)
    async def docs_login() -> HTMLResponse:
        html = """
        <!doctype html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\" />
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
            <title>License Manager API – Swagger Login</title>
            <link
            href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css\"
            rel=\"stylesheet\"
            integrity=\"sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB\"
            crossorigin=\"anonymous\"
            />
        </head>
        <body class=\"bg-light\">
            <div class=\"container py-5\">
            <div class=\"row justify-content-center\">
                <div class=\"col-12 col-md-10 col-lg-7 col-xl-6\">
                <div class=\"card shadow-sm border-0\">
                    <div class=\"card-body p-4 p-md-5\">
                    <div class=\"d-flex align-items-center gap-3 mb-3\">
                        <div
                        class=\"bg-primary text-white rounded-circle d-flex
                        align-items-center justify-content-center\"
                        style=\"width: 44px; height: 44px\"
                        >
                        <span class=\"fw-semibold\">API</span>
                        </div>
                        <div>
                        <h1 class=\"h4 mb-1\">API Docs Login</h1>
                        <p class=\"text-muted mb-0\">
                            Provide your JWT (Bearer token) to open Swagger UI.
                        </p>
                        </div>
                    </div>
                    <form id=\"login-form\" class=\"mt-4\">
                        <div class=\"mb-3\">
                        <label for=\"token\" class=\"form-label fw-semibold\"
                            >Token</label
                        >
                        <input
                            id=\"token\"
                            name=\"token\"
                            type=\"password\"
                            class=\"form-control font-monospace\"
                            placeholder=\"eyJhbGciOi...\"
                            autocomplete=\"off\"
                            required
                        />
                        <div id=\"token-status\" class=\"form-text text-muted d-none\">
                        Saved token detected. You can continue without re-entering.
                        </div>
                        </div>
                        <div class=\"d-flex flex-wrap gap-2\">
                        <button type=\"submit\" class=\"btn btn-primary\">
                            Go to Swagger UI
                        </button>
                        <button type=\"button\" id=\"redoc\" class=\"btn btn-outline-primary\">
                            Go to ReDoc
                        </button>
                        <button
                            type=\"button\"
                            id=\"logout\"
                            class=\"btn btn-outline-secondary\"
                        >
                            Logout
                        </button>
                        </div>
                        <div class=\"alert alert-secondary mt-4 mb-0 small\" role=\"alert\">
                        The token will be stored in a <code>docs_token</code> cookie
                        for this domain (valid for ten hours).
                        </div>
                    </form>
                    </div>
                </div>
                <p class=\"text-center text-muted small mt-3 mb-0\">
                    License Manager • Internal access only
                </p>
                </div>
            </div>
            </div>
            <script>
            const form = document.getElementById(\"login-form\");
            const input = document.getElementById(\"token\");
            form.noValidate = true;
            const statusEl = document.getElementById(\"token-status\");
            const defaultPlaceholder = input.getAttribute(\"placeholder\") || \"\";
            const redocBtn = document.getElementById(\"redoc\");
            const logoutBtn = document.getElementById(\"logout\");
            const cookieName = \"docs_token\";
            function getCookie(name) {
                const cookies = document.cookie ? document.cookie.split(\"; \") : [];
                for (const item of cookies) {
                const idx = item.indexOf(\"=\");
                const key = idx > -1 ? item.slice(0, idx) : item;
                if (key === name) {
                    return decodeURIComponent(item.slice(idx + 1));
                }
                }
                return null;
            }
            let cachedToken = getCookie(cookieName);
            if (cachedToken) {
                if (statusEl) {
                statusEl.classList.remove(\"d-none\");
                }
                input.placeholder = \"Token saved in browser\";
            }
            function saveToken() {
                const t = (input.value || \"\").trim() || cachedToken;
                if (!t) {
                alert(\"Provide a token\");
                return null;
                }
                const maxAge = 60 * 60 * 10;
                document.cookie =
                cookieName +
                \"=\" +
                encodeURIComponent(t) +
                \"; Max-Age=\" +
                maxAge +
                \"; Path=/; SameSite=Lax\";
                cachedToken = t;
                if (statusEl) {
                statusEl.classList.remove(\"d-none\");
                }
                return t;
            }
            form.addEventListener(\"submit\", function (e) {
                e.preventDefault();
                if (!saveToken()) {
                return;
                }
                window.location.href = \"/docs/swagger\";
            });
            redocBtn.addEventListener(\"click\", function () {
                if (!saveToken()) {
                return;
                }
                window.location.href = \"/docs/redoc\";
            });
            logoutBtn.addEventListener(\"click\", function () {
                document.cookie = cookieName + \"=; Max-Age=0; Path=/; SameSite=Lax\";
                cachedToken = null;
                input.placeholder = defaultPlaceholder;
                if (statusEl) {
                statusEl.classList.add(\"d-none\");
                }
                alert(\"Logged out.\");
            });
            </script>
            <script
            src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js\"
            integrity=\"sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI\"
            crossorigin=\"anonymous\"
            ></script>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

    @app.get("/docs/oauth2-redirect.html", include_in_schema=False)
    def swagger_ui_redirect() -> HTMLResponse:
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/health", tags=["meta"], response_model=HealthOut)
    async def health(response: Response) -> HealthOut:
        result = await HealthCheckService(app).get_health()
        if result.status != HealthOverallStatus.OK:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthOut.model_validate(result.model_dump(mode="json"))

    app.state.keycloak = idp

    return app


app = create_app()
