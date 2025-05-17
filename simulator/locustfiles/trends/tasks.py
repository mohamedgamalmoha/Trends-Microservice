import json

from locust import SequentialTaskSet, task

from locustfiles.comman.conf import settings
from locustfiles.comman.auth import AuthTaskMixin
from locustfiles.trends.models import Trends
from locustfiles.trends.factories import TrendsCreateFactory


class TrendsTasks(AuthTaskMixin, SequentialTaskSet):
    trends_url_path: str = settings.TRENDS_SERVICE_PATH

    def __init__(self, parent):
        super().__init__(parent)
        current_trends: Trends = None

    @task(2)
    def create_trends(self):
        trends_data = TrendsCreateFactory.build()
        with self.client.post(
                self.trends_url_path,
                headers=self.get_auth_headers(),
                json=trends_data,
                catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    response_data = json.loads(response.text)
                    trends_data.update(response_data)
                    self.current_trends = Trends(**trends_data)
                    response.success()
                except json.JSONDecodeError:
                    response.failure("Create new trends has invalid json schema")
                    self.interrupt()
            else:
                response.failure(
                    f"Invalid trends creation with status:{response.status_code}, and response: {response.text}"
                )
                self.interrupt()

    @task(5)
    def get_trends_by_id(self):
        if self.current_trends is None:
            self.interrupt()
            return

        with self.client.get(
                f"{self.trends_url_path}{self.current_trends.user_id}/task/{self.current_trends.task_id}/",
                headers=self.get_auth_headers(),
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Invalid get trends by id with status: {response.status_code}, and with response: {response.text}"
                )
                self.interrupt()

    @task(8)
    def get_list_trends(self):
        if self.current_trends is None:
            self.interrupt()
            return

        with self.client.get(
                f"{self.trends_url_path}{self.current_trends.user_id}/",
                headers=self.get_auth_headers(),
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Invalid get my account with status: {response.status_code}, and with response: {response.text}"
                )
                self.interrupt()

    @task(1)
    def delete_trends(self):
        if self.current_trends is None:
            self.interrupt()
            return

        with self.client.delete(
                f"{self.trends_url_path}/{self.current_trends.user_id}/task/{self.current_trends.task_id}",
                headers=self.get_auth_headers(),
                catch_response=True
        ) as response:
            if response.status_code == 204:
                response.success()
            else:
                response.failure(
                    f"Invalid delete trends with status: {response.status_code}, and with response: {response.text}"
                )
                self.interrupt()
