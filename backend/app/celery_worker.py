from celery import Celery

from app.core import get_settings
from app.tasks import *

celery_worker = Celery(
    broker=str(get_settings().CELERY_BROKER), backend=str(get_settings().CELERY_BACKEND)
)
celery_worker.set_default()
