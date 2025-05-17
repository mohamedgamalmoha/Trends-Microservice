import json
from typing import Type
from dataclasses import dataclass

import factory
from locust.clients import HttpSession
from requests.exceptions import RequestException

from locustfiles.comman.user import User, UserCreateFactory


@dataclass
class AuthManager:
    user_create_url_path: str = "/api/v1/users/"
    user_auth_url_path: str = "/api/v1/jwt/create/"
    user_auth_token_keyword: str = "token"
    user_create_factory: Type[factory.Factory] = UserCreateFactory

    @staticmethod
    def get_auth_headers(auth_token: str) -> dict:
        return {"Authorization": f"Bearer {auth_token}"}

    def get_user_create_data(self, **fields) -> dict:
        factory_class = self.user_create_factory
        user_data = factory_class.build(
            ** fields
        )
        return user_data

    @staticmethod
    def get_user_auth_data(user: User) -> dict:
        return {
            "email": user.email,
            "password": user.password
        }

    def create_user(self, client: HttpSession, **fields) -> User:
        user_data = self.get_user_create_data(**fields)

        with client.post(
                url=self.user_create_url_path,
                json=user_data,
                catch_response=True
        ) as response:

            if response.status_code == 200:
                response_data = json.loads(response.text)
                user_data.update(response_data)
                user_data.pop('password_confirm', None)
                return User(
                    **user_data
                )

            response.failure(f"User creation failed with status: {response.status_code}")
            raise RequestException(
                f"Invalid user creation with status: {response.status_code} & response: {response.text}"
            )

    def auth_user(self, client: HttpSession, user: User) -> str:
        auth_data = self.get_user_auth_data(user=user)

        with client.post(
                url=self.user_auth_url_path,
                json=auth_data,
                catch_response=True
        ) as response:

            if response.status_code == 200:
                response_data = json.loads(response.text)
                if self.user_create_factory not in response_data:
                    response.failure("Token keyword not found in response")
                    raise RequestException(
                        f"Token keyword '{self.user_auth_token_keyword}' not found in response: {response.text}"
                    )
                return response_data[self.user_auth_token_keyword]

            response.failure(f"User authentication failed with status: {response.status_code}")
            raise RequestException(
                f"Invalid user authentication with status: {response.status_code} & response: {response.text}"
            )
