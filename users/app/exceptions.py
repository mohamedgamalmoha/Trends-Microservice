from shared_utils import messages


class InvalidUserCredentials(Exception):
    message = messages.INVALID_CREDENTIALS_MESSAGE


class TokenError(Exception):
    ...


class InvalidTokenError(TokenError):
    message = messages.INVALID_TOKEN_MESSAGE


class TokenExpiredError(TokenError):
    message = messages.EXPIRED_TOKEN_MESSAGE
