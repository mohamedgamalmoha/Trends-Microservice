from locust import FastHttpUser, between

from locustfiles.comman.conf import settings
from locustfiles.users.tasks import UserTasks
from locustfiles.trends.tasks import TrendsTasks
from locustfiles.thinker.tasks import ThinkerTasks


class User(FastHttpUser):
    host = settings.USER_SERVICE_URL
    tasks = [UserTasks]
    wait_time = between(
        min_wait=settings.MIN_WAITING_TIME,
        max_wait=settings.MAX_WAITING_TIME
    )


class TrendsUser(FastHttpUser):
    host = settings.TRENDS_SERVICE_URL
    tasks = [TrendsTasks]
    wait_time = between(
        min_wait=settings.MIN_WAITING_TIME,
        max_wait=settings.MAX_WAITING_TIME
    )


class ThinkerUser(FastHttpUser):
    host = settings.USER_SERVICE_URL
    tasks = [ThinkerTasks]
    wait_time = between(
        min_wait=settings.MIN_WAITING_TIME,
        max_wait=settings.MAX_WAITING_TIME
    )
