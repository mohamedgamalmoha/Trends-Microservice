import datetime

import pydantic


class User(pydantic.BaseModel):
    id: int
    email: pydantic.EmailStr
    username: str
    first_name: str
    last_name: str
    phone_number: str
    is_active: bool
    is_admin: bool
    date_created: datetime.datetime
