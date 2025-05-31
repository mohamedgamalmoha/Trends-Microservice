import hmac
import hashlib
from typing import Union
from functools import partial

from app.core.conf import settings


type _DigestMod = Union[str, hashlib.sha256, hashlib.sha512, hashlib.md5]


def _create_signature(
        message: str,
        key: str,
        digestmod: _DigestMod
    ) -> str:
    """
    Create a HMAC signature for the given message using the specified key and digest method.

    Args:
        - message (str): The message to sign.
        - key (str): The secret key used for signing.
        - digestmod (_DigestMod): The hash function to use (e.g., hashlib.sha256).

    Returns:
        - str: The hexadecimal HMAC signature.
    """

    signature = hmac.new(
        key=key.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=digestmod
    ).hexdigest()

    return signature


def _verify_signature(
        message: str,
        signature: str,
        key: str,
        digestmod: _DigestMod
    ) -> bool:
    """
    Verify the HMAC signature for the given message using the specified key and digest method.

    Args:
        - message (str): The original message.
        - signature (str): The HMAC signature to verify.
        - key (str): The secret key used for signing.
        - digestmod (_DigestMod): The hash function to use (e.g., hashlib.sha256).

    Returns:
        - bool: True if the signature is valid, False otherwise.
    """

    expected_signature = _create_signature(
        message=message,
        key=key,
        digestmod=digestmod
    )

    return hmac.compare_digest(
        expected_signature,
        signature
    )


create_task_signature = partial(
    _create_signature,
    key=settings.TASK_SIGNATURE_KEY,
    digestmod=hashlib.sha256
)

verify_task_signature = partial(
    _verify_signature,
    key=settings.TASK_SIGNATURE_KEY,
    digestmod=hashlib.sha256
)
