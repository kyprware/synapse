"""
Handle JWT authentication logic.

This module provides a utility function to verify and decode JSON Web Tokens
based on a secret and algorithm defined in environment variables.
"""

import jwt
import logging
from os import getenv

from typing import List, Dict, Any


JWT_SECRET: str = getenv("JWT_SECRET", "secret")
JWT_ALGORITHMS: List = getenv("JWT_ALGORITHM", "HS256").split(" ")

logger: logging.Logger = logging.getLogger(__name__)


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifies and decodes a JWT token using the secret and algorithms.

    Args:
        token (str): The JWT token to verify.

    Returns:
        dict: On success, returns the decoded token claims (payload).
              On failure, returns a dict with an 'error'.
    """

    try:
        payload: Dict[str, Any] = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=JWT_ALGORITHMS
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("[AUTH] Token has expired.")
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        logger.warning("[AUTH] Invalid JWT token.")
        return {"error": "Invalid token"}
