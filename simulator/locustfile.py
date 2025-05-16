from locust import FastHttpUser, between

from locustfiles.conf import settings
from locustfiles.users.tasks import RegularUserTasks
from locustfiles.trends.tasks import TrendsTasks
from locustfiles.thinker.tasks import ThinkerTasks


class RegularUser(FastHttpUser):
    host = settings.USER_SERVICE_URL
    tasks = [RegularUserTasks, TrendsTasks, ThinkerTasks]
    wait_time = between(
        min_wait=settings.MIN_WAITING_TIME,
        max_wait=settings.MAX_WAITING_TIME
    )
