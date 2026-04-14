# License Manager Backend

Backend service for License Manager, built with FastAPI and Celery.

This project provides:
- REST API endpoints for license-management domains: customers, kinds, products, licenses, app packages, SMTP credentials, and audit logs.
- Asynchronous background processing with Celery workers and Celery Beat.
- Integrations with PostgreSQL, RabbitMQ, Keycloak, and Azure Key Vault.

## Tech Stack

- Python 3.13+
- FastAPI
- Celery
- SQLAlchemy + Alembic
- PostgreSQL
- RabbitMQ
- Keycloak
- Azure Key Vault

## Repository Layout

```text
app/license_manager/
  api/                # FastAPI app, routers, schemas
  audit/              # audit emitters
  core/               # settings and helpers
  db/                 # SQLAlchemy models, session, migration helpers
  middleware/         # request/problem/timing middlewares
  observability/      # logging setup
  repositories/       # data access layer
  services/           # business logic
  tasks/              # Celery app and workers
  templates/          # email templates

config/sample-env/    # sample environment variables
tests/                # unit tests
.vscode/              # local run/debug tasks and launch profiles
```

## Prerequisites

Install and make available:
- Python 3.13+
- PostgreSQL
- RabbitMQ
- Access to Keycloak and Azure Key Vault (or equivalent dev/test setup)

## Configuration

The app reads settings from environment variables and from `settings.dev.env` in local development.

Minimal variables typically needed for local run:
- `DATABASE_URL` (or `POSTGRES_DSN`)
- `RABBITMQ_URI`
- `KEYCLOAK_BASE_URL`
- `KEYCLOAK_REALM`
- `KEYCLOAK_CLIENT_ID`
- `KEYCLOAK_CLIENT_SECRET`
- `KEYCLOAK_ADMIN_SECRET`
- `AZURE_KEY_VAULT_URL`

You can start from `config/sample-env/.env.example`.

## Local Development

Install project dependencies:

```bash
make install
```

Run API:

```bash
make api            # uvicorn
make api-reload     # uvicorn with reload
make api-gunicorn   # gunicorn profile aligned with .vscode/launch.json
```

Run background processes:

```bash
make worker
make beat
make flower
```

Stop processes:

```bash
make stop-api
make stop-api-hard
make stop-worker
make stop-worker-hard
make stop-beat
make stop-beat-hard
make stop-flower
make stop-flower-hard
make stop-all
```

## Quality and Tests

```bash
make lint
make fmt
make test
make typecheck
```

## Database Migrations

Alembic configuration is included in this repository.

```bash
alembic upgrade head
```

On startup, migrations can also be triggered through configuration (`DB_RUN_MIGRATIONS=true`).

## API Endpoints

Base API prefix:
- `/api/v1`

Useful endpoints:
- `GET /health`
- `GET /docs/login`
- `GET /docs/swagger`
- `GET /docs/redoc`
- `GET /openapi.json` (secured)

## Deployment

Dockerfiles for API/worker/beat/flower are included in `docker/`.
If you deploy with Kubernetes/Helm, keep deployment values and release flow in your deployment repository.

## License

Proprietary - HRBN.
