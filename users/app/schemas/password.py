import pydantic


class UserPasswordReset(pydantic.BaseModel):
    email: pydantic.EmailStr


class UsePasswordResetConfirmation(pydantic.BaseModel):
    new_password: str
    new_password_confirm: str
    reset_token: str

    @pydantic.model_validator(mode='after')
    def verify_password_match(self):
        if self.new_password != self.new_password_confirm:
            raise ValueError("The two passwords did not match.")
        return self
