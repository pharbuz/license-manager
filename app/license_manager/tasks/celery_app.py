from __future__ import annotations

from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging as celery_setup_logging
from kombu import Queue

from app.license_manager.core.settings import Settings, get_settings
from app.license_manager.observability.logging import get_logger
from app.license_manager.observability.logging import setup_logging as setup_app_logging

logger = get_logger(__name__)


def _parse_cron_expression(expression: str) -> crontab:
    parts = expression.split()
    if len(parts) != 5:
        raise ValueError(
            "Cron expression must have 5 fields: minute hour day_of_month month day_of_week"
        )

    minute, hour, day_of_month, month_of_year, day_of_week = parts
    return crontab(
        minute=minute,
        hour=hour,
        day_of_month=day_of_month,
        month_of_year=month_of_year,
        day_of_week=day_of_week,
    )


def configure_beat_schedule(celery_app_instance: Celery, settings: Settings) -> None:
    if settings.LICENSE_CHECK_CRON:
        try:
            celery_app_instance.conf.beat_schedule["license-checker"] = {
                "task": (
                    "app.license_manager.tasks.workers.license_background_jobs."
                    "check_license_expirations"
                ),
                "schedule": _parse_cron_expression(settings.LICENSE_CHECK_CRON),
                "options": {"queue": settings.CELERY_TASK_DEFAULT_QUEUE},
            }
        except ValueError:
            logger.exception(
                "Invalid LICENSE_CHECK_CRON expression",
                extra={"cron": settings.LICENSE_CHECK_CRON},
            )

    if settings.LICENSE_ARCHIVER_CRON:
        try:
            celery_app_instance.conf.beat_schedule["license-archiver"] = {
                "task": (
                    "app.license_manager.tasks.workers.license_background_jobs."
                    "archive_expired_licenses"
                ),
                "schedule": _parse_cron_expression(settings.LICENSE_ARCHIVER_CRON),
                "options": {"queue": settings.CELERY_TASK_DEFAULT_QUEUE},
            }
        except ValueError:
            logger.exception(
                "Invalid LICENSE_ARCHIVER_CRON expression",
                extra={"cron": settings.LICENSE_ARCHIVER_CRON},
            )


settings = get_settings()

celery_app = Celery(
    "license_manager",
    broker=settings.CELERY_BROKER_URL or "amqp://guest:guest@localhost:5672//",
    backend=settings.CELERY_RESULT_BACKEND or "rpc://",
    include=[
        "app.license_manager.tasks.workers.audit",
        "app.license_manager.tasks.workers.email_background_jobs",
        "app.license_manager.tasks.workers.license_background_jobs",
    ],
)

celery_app.conf.task_default_queue = settings.CELERY_TASK_DEFAULT_QUEUE
celery_app.conf.task_queues = (
    Queue(settings.CELERY_TASK_DEFAULT_QUEUE),
    Queue("audit_logs"),
)
celery_app.conf.task_routes = [
    ("app.license_manager.tasks.workers.audit.*", {"queue": "audit_logs"}),
]
celery_app.conf.beat_schedule = {}

configure_beat_schedule(celery_app, settings)


@celery_setup_logging.connect
def configure_celery_logging(*args, **kwargs) -> None:
    setup_app_logging(level=kwargs.get("loglevel"))
