"""
Shared validation functions for SQLAlchemy models and schemas.
"""

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
