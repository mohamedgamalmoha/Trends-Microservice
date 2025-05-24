import json

from locust import SequentialTaskSet, task

from locustfiles.comman.conf import settings
from locustfiles.comman.auth import AuthTaskMixin
from locustfiles.think.models import Think
from locustfiles.think.factories import ThinkCreateFactory


class ThinkTasks(AuthTaskMixin, SequentialTaskSet):
    think_url_path: str = settings.THINK_SERVICE_PATH

    def __init__(self, parent):
        super().__init__(parent)
        self.current_think: Think = None

    @task(2)
    def create_think(self):
        thinker_data = ThinkCreateFactory.build(user_id=self.current_user.id)
        with self.client.post(
                f"{self.think_url_path}task/",
                headers=self.get_auth_headers(),
                json=thinker_data,
                catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    response_data = json.loads(response.text)
                    thinker_data.update(response_data)
                    self.current_think = Think(**thinker_data)
                    response.success()
                except json.JSONDecodeError:
                    response.failure("Create new thinker has invalid json schema")
                    self.interrupt()
            else:
                response.failure(
                    f"Invalid thinker creation with status:{response.status_code}, and response: {response.text}"
                )
                self.interrupt()

    @task(5)
    def get_think_by_id(self):
        if self.current_think is None:
            self.interrupt()
            return

        with self.client.get(
                f"{self.think_url_path}{self.current_user.id}/task/{self.current_think.task_id}/",
                headers=self.get_auth_headers(),
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Invalid get thinker by id with status: {response.status_code}, and with response: {response.text}"
                )
                self.interrupt()

    @task(8)
    def get_list_think(self):
        if self.current_think is None:
            self.interrupt()
            return

        with self.client.get(
                f"{self.think_url_path}{self.current_user.id}/tasks/",
                headers=self.get_auth_headers(),
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Invalid get my thinker with status: {response.status_code}, and with response: {response.text}"
                )
                self.interrupt()

    @task(1)
    def delete_think(self):
        if self.current_think is None:
            self.interrupt()
            return

        with self.client.delete(
                f"{self.think_url_path}{self.current_user.id}/task/{self.current_think.task_id}",
                headers=self.get_auth_headers(),
                catch_response=True
        ) as response:
            if response.status_code == 204:
                response.success()
            else:
                response.failure(
                    f"Invalid delete thinker with status: {response.status_code}, and with response: {response.text}"
                )
                self.interrupt()
