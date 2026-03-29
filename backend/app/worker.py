from celery import Celery
from celery.schedules import crontab
from app.core import get_settings

celery_worker = Celery(
    broker=str(get_settings().CELERY_BROKER),
    backend=str(get_settings().CELERY_BACKEND),
    include=["app.tasks"],
)
celery_worker.conf.timezone = "UTC"

# delete document that:
# - have been soft deleted for over 30days
# - have been banned for over 30days
celery_worker.conf.beat_schedule = {
    'delete-old-docs-daily': {
        'task': 'app.tasks.document_task.auto_delete_document_task',
        'schedule': crontab(minute=0, hour=0),
    }
}
celery_worker.set_default()
