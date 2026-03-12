from celery import Celery

from app.core import settings
from app.tasks import *

celery_worker = Celery(
    broker=str(settings.CELERY_BROKER), backend=str(settings.CELERY_BACKEND)
)
celery_worker.set_default()
