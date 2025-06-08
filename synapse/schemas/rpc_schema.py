"""
Schemas for JSON-RPC requests and responses.
"""

from pydantic import BaseModel, field_validator

from typing import Optional, Union, Any

from .shared.validators import (
    validate_jwt,
    validate_uuid,
    validate_jsonrpc_version,
    validate_jsonrpc_2_error_codes
)


class RPCRequest(BaseModel):
    """
    Base schema for authenticated JSON-RPC requests.
    """

    jsonrpc: str = "2.0"
    id: Union[str, None]
    method: str
    params: Optional[dict[str, Any]] = None
    authorization_token: str

    @field_validator("jsonrpc")
    @classmethod
    def jsonrpc_validator(cls, v: str) -> str:
        return validate_jsonrpc_version(cls, v)

    @field_validator("id")
    @classmethod
    def uuid_validator(cls, v: Union[str, None]) -> Union[str, None]:
        if not v:
            return None

        return validate_uuid(cls, v)

    @field_validator("authorization_token")
    @classmethod
    def authorization_token_validator(cls, v: str) -> str:
        return validate_jwt(cls, v)


class RPCError(BaseModel):
    """
    Standard JSON-RPC error format.
    """

    code: int
    message: str
    data: Optional[Union[list[Any], dict[str, Any]]] = None

    @field_validator("code")
    @classmethod
    def code_validator(cls, v: int) -> int:
        return validate_jsonrpc_2_error_codes(cls, v)


class RPCResponse(BaseModel):
    """
    Standard JSON-RPC response.
    """

    jsonrpc: str = "2.0"
    id: Union[str, None]
    result: Optional[Any] = None
    error: Optional[RPCError] = None

    @field_validator("jsonrpc")
    @classmethod
    def jsonrpc_validator(cls, v: str) -> str:
        return validate_jsonrpc_version(cls, v)

    @field_validator("id")
    @classmethod
    def uuid_validator(cls, v: Union[str, None]) -> Union[str, None]:
        if not v:
            return None

        return validate_uuid(cls, v)


class RPCNotification(BaseModel):
    """
    Base schema for JSON-RPC notification.
    """

    jsonrpc: str = "2.0"
    method: str
    params: Optional[dict[str, Any]] = None

    @field_validator("jsonrpc")
    @classmethod
    def jsonrpc_validator(cls, v: str) -> str:
        return validate_jsonrpc_version(cls, v)
