import pydantic


class UserPasswordReset(pydantic.BaseModel):
    email: pydantic.EmailStr


class UsePasswordResetConfirmation(pydantic.BaseModel):
    reset_token: str
