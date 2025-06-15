"""
Shared validation functions for SQLAlchemy models and other components.
"""

import base64
from uuid import UUID

from typing import List

from urllib.parse import urlparse, ParseResult


def validate_jsonrpc_version(key: str, value: str) -> str:
    """
    Validates that the JSON-RPC version is '2.0'.

    Args:
        key (str): The field name being validated
        value (str): The version string to validate

    Returns:
        str: The validated version string

    Raises:
        ValueError: If the version is not '2.0'
    """

    if value != "2.0":
        raise ValueError(f"Invalid JSON-RPC version '{value}' for '{key}'")

    return value


def validate_uuid(key: str, value: str) -> str:
    """
    Validates that the input string is a valid UUID format.

    Args:
        key (str): The field name being validated
        value (str): The UUID string to validate

    Returns:
        str: The validated UUID string

    Raises:
        ValueError: If the string is not a valid UUID format
    """

    try:
        UUID(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid UUID format for field '{key}': '{value}'")
    return value


def validate_jwt(key: str, value: str) -> str:
    """
    Validates that a string has the structure of a valid JWT token.
    Checks for 3 base64-encoded parts separated by dots.

    Args:
        key (str): The field name being validated
        value (str): The JWT string to validate

    Returns:
        str: The validated JWT string

    Raises:
        ValueError: If the JWT is invalid or parts are not base64-encoded
    """

    parts: List[str] = value.split('.')

    if len(parts) != 3:
        raise ValueError(f"Invalid JWT format for '{key}'")

    for i, part in enumerate(parts):
        try:
            padding: str = '=' * (-len(part) % 4)
            base64.urlsafe_b64decode(part + padding)
        except Exception:
            raise ValueError(
                f"Invalid base64 encoding in JWT part {i+1} for field '{key}'"
            )

    return value


def validate_jsonrpc_error_codes(key: str, value: int) -> int:
    """
    Validates that an error code conforms to the JSON-RPC 2.0 specification.

    Args:
        key (str): The field name being validated
        value (int): The error code to validate

    Returns:
        int: The validated error code

    Raises:
        ValueError: If the error code is not a valid JSON-RPC 2.0 error code
    """

    VALID_JSONRPC_2_ERROR_CODES: list[int] = [
        -32700,  # Parse error
        -32600,  # Invalid Request
        -32601,  # Method not found
        -32602,  # Invalid params
        -32603,  # Internal error
        *range(-32099, -32000 + 1)  # Server error range (inclusive)
    ]

    if value not in VALID_JSONRPC_2_ERROR_CODES:
        raise ValueError(
            f"Invalid JSON-RPC 2.0 error code for '{key}': {value}"
        )

    return value


def validate_url(key: str, value: str) -> str:
    """
    Validates that a string is a URL with both scheme and network location.

    Args:
        key (str): The field name being validated
        value (str): The URL string to validate

    Returns:
        str: The validated URL string

    Raises:
        ValueError: If the URL is malformed or missing required components
    """

    parsed: ParseResult = urlparse(value)

    if not (parsed.scheme and parsed.netloc):
        missing_parts = []

        if not parsed.scheme:
            missing_parts.append("scheme")
        if not parsed.netloc:
            missing_parts.append("domain")
        raise ValueError(f"Invalid URL format for '{key}': '{value}'")

    return value
