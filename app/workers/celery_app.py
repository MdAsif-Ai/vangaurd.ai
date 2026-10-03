"""Celery application (Redis broker and result backend)."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "financerag",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)
