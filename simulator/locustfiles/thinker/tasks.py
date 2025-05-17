import json

from locust import SequentialTaskSet, task

from locustfiles.comman.auth import AuthTaskMixin
from locustfiles.thinker.models import Thinker
from locustfiles.thinker.factories import ThinkerCreateFactory


class ThinkerTasks(AuthTaskMixin, SequentialTaskSet):

    def __init__(self, parent):
        super().__init__(parent)
        current_thinker: Thinker = None

    @task(2)
    def create_thinker(self):
        thinker_data = ThinkerCreateFactory.build()
        with self.client.post(
                "/api/v1/think/",
                headers=self.get_auth_headers(),
                json=thinker_data,
                catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    response_data = json.loads(response.text)
                    thinker_data.update(response_data)
                    self.current_thinker = Thinker(**thinker_data)
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
    def get_thinker_by_id(self):
        if self.current_thinker is None:
            self.interrupt()
            return

        with self.client.get(
                f"/api/v1/think/{self.current_thinker.user_id}/task/{self.current_thinker.task_id}/",
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
    def get_list_thinker(self):
        if self.current_thinker is None:
            self.interrupt()
            return

        with self.client.get(
                f"/api/v1/think/{self.current_thinker.user_id}/",
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
    def delete_thinker(self):
        if self.current_thinker is None:
            self.interrupt()
            return

        with self.client.delete(
                f"/api/v1/think/{self.current_thinker.user_id}/task/{self.current_thinker.task_id}",
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
