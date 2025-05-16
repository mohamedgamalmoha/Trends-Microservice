import json
from requests.exceptions import RequestException

from locustfiles.comman.user import User
from locustfiles.comman.auth.manager import AuthManager


class AuthTaskMixin:

    def __init__(self, parent):
        super().__init__(parent)
        self.auth_manage: AuthManager = AuthManager(
            ** self.get_auth_manager_init_keyword()
        )
        self.current_user: User = None
        self.auth_token: str = None

    def get_auth_manager_init_keyword(self) -> dict:
        return {}

    def on_start(self) -> None:
        self.current_user = self.create_user()
        self.auth_token = self.auth_user(user=self.current_user)

    def create_user(self, **fields) -> User:
        try:
            user = self.auth_manager.create_user(client=self.client, **fields)
            return user
        except (json.JSONDecodeError, RequestException):
            self.interrupt()

    def auth_user(self, user: User) -> str:
        try:
            auth_token = self.auth_manager.auth_user(client=self.client, user=user)
            return auth_token
        except (json.JSONDecodeError, RequestException):
            self.interrupt()

    def get_auth_headers(self) -> dict:
        return self.auth_manager.get_auth_headers(auth_token=self.auth_token)
