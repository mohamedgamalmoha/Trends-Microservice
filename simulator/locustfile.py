from locust import FastHttpUser, between

from locustfiles.conf import settings
from locustfiles.users.tasks import RegularUserTasks


class RegularUser(FastHttpUser):
    host = settings.USER_SERVICE_URL
    tasks = [RegularUserTasks]
    wait_time = between(
        min_wait=settings.MIN_WAITING_TIME,
        max_wait=settings.MAX_WAITING_TIME
    )
