from shared_utils import messages


class TokenError(Exception):
    ...


class InvalidTokenError(TokenError):
    message = messages.INVALID_TOKEN_MESSAGE


class TokenExpiredError(TokenError):
    message = messages.EXPIRED_TOKEN_MESSAGE
