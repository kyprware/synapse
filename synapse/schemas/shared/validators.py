"""
Shared schema validation modules
"""

import base64
from uuid import UUID
from urllib.parse import urlparse

from typing import List, Any
from urllib.parse import ParseResult


def validate_jsonrpc_version(_, v: str) -> str:
    """
    Validates that the jsonrpc version is supported
    """

    if v != "2.0":
        raise ValueError("JSON-RPC version is not supported")

    return v


def validate_uuid(_, v: str) -> str:
    """
    Validates that the input string is a valid UUID.
    """

    try:
        UUID(v)
    except (ValueError, TypeError):
        raise ValueError("Invalid UUID string")

    return v


def validate_jwt(_: Any, v: str) -> str:
    """
    Validates that a string is a properly formatted JWT token.
    """

    parts: List = v.split('.')

    if len(parts) != 3:
        raise ValueError("JWT must have exactly 3 parts separated by '.'")

    for part in parts:
        try:
            padding: str = '=' * (-len(part) % 4)
            base64.urlsafe_b64decode(part + padding)
        except Exception:
            raise ValueError("Invalid Base64 encoding in JWT")

    return v



def validate_jsonrpc_2_error_codes(_, v: int) -> int:
    """
    Validates JSON-RPC error code.
    """

    VALID_JSONRPC_2_ERROR_CODES: list[int] = [
        -32700,  # Parse error
        -32600,  # Invalid Request
        -32601,  # Method not found
        -32602,  # Invalid params
        -32603,  # Internal error
        *range(-32099, -32000 + 1)  # Server error range (inclusive)
    ]

    if not v in VALID_JSONRPC_2_ERROR_CODES:
        raise ValueError("Invalid JSON RPC V2.0 error code")

    return v


def validate_url(_, v: str) -> str:
    """
    Validates that the input string is a well-formed URL.
    """

    parsed: ParseResult = urlparse(v)

    if not (parsed.scheme and parsed.netloc):
        raise ValueError("Invalid URL format")

    return v
