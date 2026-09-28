"""Background tasks.

Phase 1 contains a single health check task. Ingestion and research
tasks arrive in later phases.
"""

from app.core.config import get_settings
from app.workers.celery_app import celery_app


@celery_app.task(name="financerag.health_check")
def health_check_task() -> dict[str, str]:
    """Prove the worker can consume tasks (and reach the Redis broker)."""
    settings = get_settings()
    return {
        "status": "ok",
        "service": "financerag-worker",
        "app_env": settings.app_env,
    }