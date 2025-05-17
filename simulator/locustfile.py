from locust import FastHttpUser, between

from locustfiles.comman.conf import settings
from locustfiles.users.tasks import UserTasks
from locustfiles.trends.tasks import TrendsTasks
from locustfiles.think.tasks import ThinkTasks


class User(FastHttpUser):
    host = settings.SERVICE_BASE_URL
    tasks = [UserTasks]
    wait_time = between(
        min_wait=settings.MIN_WAITING_TIME,
        max_wait=settings.MAX_WAITING_TIME
    )


class TrendsUser(FastHttpUser):
    host = settings.SERVICE_BASE_URL
    tasks = [TrendsTasks]
    wait_time = between(
        min_wait=settings.MIN_WAITING_TIME,
        max_wait=settings.MAX_WAITING_TIME
    )


class ThinkUser(FastHttpUser):
    host = settings.SERVICE_BASE_URL
    tasks = [ThinkTasks]
    wait_time = between(
        min_wait=settings.MIN_WAITING_TIME,
        max_wait=settings.MAX_WAITING_TIME
    )
