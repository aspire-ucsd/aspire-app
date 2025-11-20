""" This file stores the functions that allow for Anonymization of Information."""
import hmac
import hashlib

from app.config.environment import get_secret_key

# TODO: Automate key retrieval from lockbox when infrastructure is in place.
def hash_string_using_sha256(input: str, key: str = get_secret_key()) -> str:
    """ This function hashes the given input using the SHA256 hashing function.

    Args:
        key: Secret key to maintain consistent and replicable hashing of input.
        input: The string field that needs to be hashed.

    Returns:
        A 64 character long hexadecimal string that contains the hash value.
    """

    return hmac.new(
        key=key.encode(),
        msg=input.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
