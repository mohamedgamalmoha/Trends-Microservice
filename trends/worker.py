from celery import Celery

from app.core.conf import settings


celery = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.celery.tasks']
)

celery.conf.task_routes = {'trends.*': {'queue': 'trends_queue'}}
celery.conf.task_default_queue = 'trends_queue'
celery.conf.task_default_exchange = 'trends_exchange'
celery.conf.task_default_routing_key = 'trends_routing_key'
celery.conf.broker_connection_retry_on_startup = True
