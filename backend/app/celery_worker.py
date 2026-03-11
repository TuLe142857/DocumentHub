from celery import Celery

from app.core import settings
from app.tasks import *

celery_worker = Celery(
    broker=str(settings.get_redis_url(1)), backend=str(settings.get_redis_url(1))
)
celery_worker.set_default()
