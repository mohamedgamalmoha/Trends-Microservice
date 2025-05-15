import json

from locust import SequentialTaskSet, task

from locustfiles.users.models import User
from locustfiles.users.factories import UserCreateFactory, UserUpdateFactory


class RegularUserTasks(SequentialTaskSet):

    def __init__(self, parent):
        super().__init__(parent)
        self.current_user: User = None
        self.auth_token: str = None

    def get_headers(self):
        return {"Authorization": f"Bearer {self.auth_token}"}

    @task(1)
    def create(self):
        user_data = UserCreateFactory.build()

        with self.client.post(
                "/api/v1/users/",
                json=user_data,
                catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    response_data = json.loads(response.text)
                    user_data.update(response_data)
                    user_data.pop('password_confirm', None)
                    self.current_user = User(**user_data)
                    response.success()
                except json.JSONDecodeError:
                    response.failure("Create new user has invalid json schema")
                    self.interrupt()
            else:
                response.failure(
                    f"Invalid user creation with status:{response.status_code}, and response: {response.text}")
                self.interrupt()

    @task(2)
    def login(self):
        # Ensure current_user is not None before proceeding
        if self.current_user is None:
            self.interrupt()
            return

        with self.client.post(
                "/api/v1/jwt/create/",
                json={
                    "email": self.current_user.email,
                    "password": self.current_user.password
                },
                catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    response_data = json.loads(response.text)
                    self.auth_token = response_data.get("token")

                    if not self.auth_token:
                        response.failure("Login succeeded but no auth token in response")
                        self.interrupt()
                    else:
                        response.success()
                except json.JSONDecodeError:
                    response.failure("Login response not valid JSON")
                    self.interrupt()
            else:
                response.failure(f"Login failed with status code: {response.status_code}")
                self.interrupt()

    @task(3)
    def get_me(self):
        # Ensure auth_token is not None before proceeding
        if self.auth_token is None:
            self.interrupt()
            return

        with self.client.get(
                "/api/v1/users/me/",
                headers=self.get_headers(),
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Invalid get my account with status: {response.status_code}, and with response: {response.text}")
                self.interrupt()

    @task(4)
    def get_by_id(self):
        # Ensure auth_token is not None before proceeding
        if self.auth_token is None:
            self.interrupt()
            return

        with self.client.get(
                f"/api/v1/users/{self.current_user.id}/",
                headers=self.get_headers(),
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Invalid get my account with status: {response.status_code}, and with response: {response.text}")
                self.interrupt()

    @task(5)
    def update(self):
        update_data = UserUpdateFactory.build()
        with self.client.put(
                f"/api/v1/users/{self.current_user.id}/",
                headers=self.get_headers(),
                json=update_data,
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response_data = json.loads(response.text)
                for k, v in response_data:
                    if hasattr(self.current_user, k):
                        setattr(self.current_user, k, v)
                response.success()
            else:
                response.failure(
                    f"Invalid get my account with status: {response.status_code}, and with response: {response.text}")
                self.interrupt()
