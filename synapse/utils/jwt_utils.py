"""
JWT utility functions using a structured TokenData model.

Provides encode and decode functions with type safety and validation.
"""

import jwt
from os import getenv

from ..schemas.application_connection_schema import ApplicationSession


JWT_SECRET: str = getenv("JWT_SECRET", "secret")
JWT_ALGORITHM: str = getenv("JWT_ALGORITHM", "HS256")


def encode_token(payload: ApplicationSession) -> str:
    """
    Encodes a JWT token.

    Args:
        payload (ApplicationSession): Session data to encode.

    Returns:
        str: Encoded JWT token.
    """

    return jwt.encode(
        payload.model_dump(),
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def decode_token(token: str) -> ApplicationSession:
    """
    Decodes and verifies a JWT token.

    Args:
        token (str): The JWT token to verify.

    Returns:
        TokenData: Decoded token payload.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid.
        ValidationError: If decoded payload is invalid.
    """

    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return ApplicationSession(**decoded)
