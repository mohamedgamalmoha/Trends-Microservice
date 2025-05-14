import json

from locust import FastHttpUser, SequentialTaskSet, task, between

from conf import settings
from models import User
from factories import UserCreateFactory



class UserBehavior(SequentialTaskSet):
    user: User = None
    auth_token: str = None

    def get_headers(self):
        return {"Authorization": f"Bearer {self.auth_token}"}

    @task
    def create(self):
        user_data = UserCreateFactory.build()
        response = self.client.post(
            "/api/v1/users/",
            json=user_data,
            catch_response=True
        )

        if response.status_code == 200:
            try:
                response_data  = json.loads(
                    response.text
                )
                user_data.update(response_data)
                user_data.pop('password_confirm', None)
                self.user = User(
                    **user_data
                )
                response.success()
            except json.JSONDecodeError:
                response.failure("Create new user has invalid json schema")
                self.interrupt()
        else:
            response.failure(f"Invalid user creation with status:{response.status_code}, and response: {response.text}")
            self.interrupt()

    @task
    def login(self):
        response = self.client.post(
            "/api/v1/jwt/create/",
            json={
                "email": self.user.email,
                "password": self.user.password
            }
        )

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

    @task
    def get_me(self):
        response = self.client.get(
            "/api/v1/users/me/",
            headers=self.get_headers()
        )
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Invalid get my account with status: {response.status_code}, and with response:"
                             f" {response.text}")
            self.interrupt()


class RegularUser(FastHttpUser):
    base = settings.USER_SERVICE_URL
    tasks = [UserBehavior]
    wait_time = between(
        min_wait=settings.MIN_WAITING_TIME,
        max_wait=settings.MAX_WAITING_TIME
    )
