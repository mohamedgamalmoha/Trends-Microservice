import datetime
import pydantic


class UserCreate(pydantic.BaseModel):
    email: pydantic.EmailStr
    username: str
    first_name: str
    last_name: str
    phone_number: str
    password: str

    class Config:
       from_attributes=True


class UserLogin(pydantic.BaseModel):
    email: pydantic.EmailStr
    password: str

    class Config:
       from_attributes=True


class UserUpdate(pydantic.BaseModel):
    first_name: str
    last_name: str
    phone_number: str

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
       from_attributes=True
