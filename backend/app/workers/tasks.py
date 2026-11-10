import logging
from backend.app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.ping")
def ping_task() -> str:
    logger.info("Celery ping task executed successfully")
    return "pong"
