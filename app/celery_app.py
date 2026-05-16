from celery import Celery

from app.core.config import settings


celery_app = Celery('app')
celery_app.conf.update(
    broker_url=settings.REDIS_URL,
    result_backend=settings.REDIS_URL,
    task_default_queue='default',
    task_ignore_result=True,
    timezone='UTC',
)

import app.tasks.example  # noqa: E402, F401
