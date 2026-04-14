# ---- Makefile for License Manager ----

PYTHON ?= python3
UVICORN_APP ?= app.license_manager.api.main:create_app
CELERY_APP ?= app.license_manager.tasks.celery_app.celery_app
FLOWER_BROKER ?= amqp://guest:guest@10.224.0.13:5672/ph-dev

UVICORN_CMD ?= uvicorn $(UVICORN_APP) --factory --host 0.0.0.0 --port 8000
UVICORN_RELOAD_CMD ?= uvicorn $(UVICORN_APP) --factory --reload --host 0.0.0.0 --port 8000
GUNICORN_CMD ?= gunicorn -k uvicorn.workers.UvicornWorker app.license_manager.api.main:create_app() --bind 0.0.0.0:8000 --workers 1 --threads 1 --graceful-timeout 30 --timeout 60
CELERY_WORKER_CMD ?= celery -A $(CELERY_APP) worker -l info -n celery@10.3.0.66
CELERY_BEAT_CMD ?= celery -A $(CELERY_APP) beat -l info
CELERY_FLOWER_CMD ?= celery -A $(CELERY_APP) flower --broker=$(FLOWER_BROKER) --port=5555

.PHONY: help api api-reload api-gunicorn dev prod worker beat flower stop-api stop-api-hard stop-worker stop-worker-hard stop-beat stop-beat-hard stop-flower stop-flower-hard stop-all lint fmt test typecheck precommit install

help:
	@echo "make api              - run FastAPI with uvicorn"
	@echo "make api-reload       - run FastAPI with uvicorn --reload"
	@echo "make api-gunicorn     - run FastAPI with gunicorn (debug-friendly profile)"
	@echo "make dev              - alias for api-reload"
	@echo "make prod             - alias for api-gunicorn"
	@echo "make worker           - run Celery worker"
	@echo "make beat             - run Celery beat"
	@echo "make flower           - run Celery Flower on :5555"
	@echo "make stop-api         - stop process on port 8000 (TERM)"
	@echo "make stop-api-hard    - stop process on port 8000 (KILL)"
	@echo "make stop-worker      - stop Celery worker (TERM)"
	@echo "make stop-worker-hard - stop Celery worker (KILL)"
	@echo "make stop-beat        - stop Celery beat (TERM)"
	@echo "make stop-beat-hard   - stop Celery beat (KILL)"
	@echo "make stop-flower      - stop Flower on :5555 (TERM)"
	@echo "make stop-flower-hard - stop Flower on :5555 (KILL)"
	@echo "make stop-all         - stop API, worker, beat and flower (TERM)"
	@echo "make lint             - run ruff linter"
	@echo "make fmt              - auto-fix with ruff"
	@echo "make test             - run pytest"
	@echo "make typecheck        - run mypy"
	@echo "make precommit        - install pre-commit hooks"
	@echo "make install          - install project in editable mode"

api:
	$(UVICORN_CMD)

api-reload:
	$(UVICORN_RELOAD_CMD)

api-gunicorn:
	$(GUNICORN_CMD)

dev: api-reload

prod: api-gunicorn

worker:
	$(CELERY_WORKER_CMD)

beat:
	$(CELERY_BEAT_CMD)

flower:
	$(CELERY_FLOWER_CMD)

stop-api:
	lsof -t -i tcp:8000 | xargs -r kill -TERM

stop-api-hard:
	lsof -t -i tcp:8000 | xargs -r kill -KILL

stop-worker:
	pkill -TERM -f 'celery .* -A app\.license_manager\.tasks\.celery_app\.celery_app .* worker' || true

stop-worker-hard:
	pkill -KILL -f 'celery .* -A app\.license_manager\.tasks\.celery_app\.celery_app .* worker' || true

stop-beat:
	pkill -TERM -f 'celery .* -A app\.license_manager\.tasks\.celery_app\.celery_app .* beat' || true

stop-beat-hard:
	pkill -KILL -f 'celery .* -A app\.license_manager\.tasks\.celery_app\.celery_app .* beat' || true

stop-flower:
	lsof -t -i tcp:5555 | xargs -r kill -TERM

stop-flower-hard:
	lsof -t -i tcp:5555 | xargs -r kill -KILL

stop-all: stop-api stop-worker stop-beat stop-flower

lint:
	ruff check .

fmt:
	ruff check . --fix

test:
	pytest -q

typecheck:
	mypy app

precommit:
	pre-commit install

install:
	pip install -e '.[dev]'
