import json

from locust import SequentialTaskSet, task

from locustfiles.comman.user import User
from locustfiles.comman.auth import AuthTaskMixin
from locustfiles.users.factories import UserUpdateFactory


class UserTasks(AuthTaskMixin, SequentialTaskSet):

    def __init__(self, parent):
        super().__init__(parent)
        self.current_user: User = None
        self.auth_token: str = None

    @task(2)
    def get_me(self):
        # Ensure auth_token is not None before proceeding
        if self.auth_token is None:
            self.interrupt()
            return

        with self.client.get(
                "/api/v1/users/me/",
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

    @task(4)
    def get_by_id(self):
        # Ensure auth_token is not None before proceeding
        if self.auth_token is None:
            self.interrupt()
            return

        with self.client.get(
                f"/api/v1/users/{self.current_user.id}/",
                headers=self.get_auth_headers(),
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Invalid get my account with status: {response.status_code}, and with response: {response.text}")
                self.interrupt()

    @task(6)
    def update(self):
        update_data = UserUpdateFactory.build()
        with self.client.put(
                f"/api/v1/users/{self.current_user.id}/",
                headers=self.get_auth_headers(),
                json=update_data,
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response_data = json.loads(response.text)
                for k, v in response_data.items():
                    if hasattr(self.current_user, k):
                        setattr(self.current_user, k, v)
                response.success()
            else:
                response.failure(
                    f"Invalid get my account with status: {response.status_code}, and with response: {response.text}"
                )
                self.interrupt()
