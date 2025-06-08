"""
Handle jwt authentication logic.
"""

import jwt
from os import getenv

from typing import List, Dict, Any

JWT_SECRET: str = getenv("JWT_SECRET", "secret")
JWT_ALGORITHMS: List = getenv("JWT_ALGORITHM", "HS256").split(" ")

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifies a JWT token using a secret and algorithm.
    """

    try:
        return jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHMS)
    except jwt.ExpiredSignatureError:
        return { "error": "Token expired" }
    except jwt.InvalidTokenError:
        return { "error": "Invalid token" }
