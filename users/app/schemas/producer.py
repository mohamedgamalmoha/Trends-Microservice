from app.schemas.user import UserRetrieve


class UserCreationProducerMessage(UserRetrieve):
    ...


class UserEmailVerificationProducerMessage(UserCreationProducerMessage):
    verification_token: str


class UserEmailConfirmationProducerMessage(UserCreationProducerMessage):
    ...


class UserResetPasswordProducerMessage(UserCreationProducerMessage):
    reset_token: str


class UserResetPasswordConfirmationProducerMessage(UserCreationProducerMessage):
    ...
