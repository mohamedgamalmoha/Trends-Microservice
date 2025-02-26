import pydantic


class UserEmailVerification(pydantic.BaseModel):
    email: pydantic.EmailStr


class UserEmailVerificationConfirmation(pydantic.BaseModel):
    verification_token: str
