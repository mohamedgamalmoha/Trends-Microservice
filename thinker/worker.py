from celery import Celery

from app.core.conf import settings


celery = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.celery.tasks']
)

celery.conf.task_routes = {'thinker.*': {'queue': 'thinker_queue'}}
