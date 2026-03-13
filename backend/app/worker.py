from celery import Celery

from app.core import get_settings

celery_worker = Celery(
    broker=str(get_settings().CELERY_BROKER),
    backend=str(get_settings().CELERY_BACKEND),
    include=["app.tasks"],
)
celery_worker.set_default()
