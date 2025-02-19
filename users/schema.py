import datetime
from typing import Optional

import pydantic


class UserCreate(pydantic.BaseModel):
    email: pydantic.EmailStr
    username: str = pydantic.Field(min_length=8, max_length=200)
    first_name: str = pydantic.Field(min_length=2, max_length=200)
    last_name: str = pydantic.Field(min_length=2, max_length=200)
    phone_number: str = pydantic.Field(min_length=2, max_length=20)
    password: str =  pydantic.Field(min_length=8, max_length=20)
    password_confirm: str

    class Config:
        from_attributes=True

    @pydantic.model_validator(mode='after')
    def verify_password_match(self):
        if self.password != self.password_confirm:
            raise ValueError("The two passwords did not match.")
        return self


class AdminUserCreate(pydantic.BaseModel):
    email: pydantic.EmailStr
    username: str = pydantic.Field(min_length=8, max_length=200)
    password: str =  pydantic.Field(min_length=8, max_length=20)

    class Config:
        from_attributes=True


class UserLogin(pydantic.BaseModel):
    email: pydantic.EmailStr
    password: str

    class Config:
        from_attributes=True


class UserUpdate(pydantic.BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]

    class Config:
        from_attributes=True


class UserRetrieve(pydantic.BaseModel):
    id: int
    email: pydantic.EmailStr
    username: str
    first_name: str
    last_name: str
    phone_number: str
    is_active: bool
    is_admin: bool
    date_created: datetime.datetime

    class Config:
        from_attributes = True


class Token(pydantic.BaseModel):
    access_token: str
    token_type: Optional[str] = 'Bearer'
