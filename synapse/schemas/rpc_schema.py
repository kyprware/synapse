"""
Schemas for JSON-RPC 2.0 requests and responses.
"""

from typing import Optional, Union, Any

from pydantic import BaseModel, field_validator

from ..utils.validator_utils import (
    validate_uuid,
    validate_jsonrpc_version,
    validate_jsonrpc_error_codes
)


class RPCRequest(BaseModel):
    """
    JSON-RPC 2.0 request schema for authenticated method calls.

    Fields:
        jsonrpc (str): JSON-RPC version. Defaults to "2.0".
        id (str | None): Optional request identifier.
        method (str): Name of the method to be invoked.
        params (dict | None): Optional parameters for the method.
    """

    jsonrpc: str = "2.0"
    id: Union[str, None]
    method: str
    params: Optional[dict[str, Any]] = None

    @field_validator("jsonrpc")
    @classmethod
    def validate_jsonrpc(cls, v: str) -> str:
        return validate_jsonrpc_version("jsonrpc", v)


    @field_validator("id")
    @classmethod
    def validate_id(cls, v: Union[str, None]) -> Union[str, None]:
        return validate_uuid("id", v) if v else None


class RPCError(BaseModel):
    """
    JSON-RPC 2.0 error object schema.

    Fields:
        code (int): A predefined JSON-RPC error code.
        message (str): A human-readable error message.
        data (list | dict | None): Optional additional error information.
    """

    code: int
    message: str
    data: Optional[Union[list[Any], dict[str, Any]]] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: int) -> int:
        return validate_jsonrpc_error_codes("code", v)


class RPCResponseData(BaseModel):
    """
    JSON-RPC 2.0 response data schema.

    Fields:
        result (Any | None): Result returned by the method, if successful.
        error (RPCError | None): Error object, if an error occurred.
    """

    result: Optional[Any] = None
    error: Optional[RPCError] = None


class RPCResponse(RPCResponseData):
    """
    JSON-RPC 2.0 response schema.

    Fields:
        jsonrpc (str): JSON-RPC version. Defaults to "2.0".
        id (str | None): The ID of the request.
        result (Any | None): Result returned by the method, if successful.
        error (RPCError | None): Error object, if an error occurred.
    """

    jsonrpc: str = "2.0"
    id: Union[str, None]

    @field_validator("jsonrpc")
    @classmethod
    def validate_jsonrpc(cls, v: str) -> str:
        return validate_jsonrpc_version("jsonrpc", v)


    @field_validator("id")
    @classmethod
    def validate_id(cls, v: Union[str, None]) -> Union[str, None]:
        return validate_uuid("id", v) if v else None


class RPCNotification(BaseModel):
    """
    JSON-RPC 2.0 notification schema (no response expected).

    Fields:
        jsonrpc (str): JSON-RPC version. Defaults to "2.0".
        method (str): Name of the method to be invoked.
        params (dict | None): Optional parameters for the method.
    """

    jsonrpc: str = "2.0"
    method: str
    params: Optional[dict[str, Any]] = None

    @field_validator("jsonrpc")
    @classmethod
    def validate_jsonrpc(cls, v: str) -> str:
        return validate_jsonrpc_version("jsonrpc", v)
