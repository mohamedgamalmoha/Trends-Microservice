import datetime
from dataclasses import dataclass


@dataclass
class User:
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    phone_number: str
    is_active: bool
    is_admin: bool
    password: str
    date_created: datetime.datetime
