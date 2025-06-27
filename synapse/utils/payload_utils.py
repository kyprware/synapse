"""
Handle data encoding, decoding, and transformation for RPC transmission.

Supports JSON-RPC 2.0 over TCP using a length-prefixed binary message format.
"""

import json
import struct
import asyncio
import logging
from typing import Optional, Union, Any, Dict, cast

from pydantic import BaseModel

from ..types.rpc_types import RPCData, RPCPayload
from ..schemas.rpc_schema import (
    RPCNotification,
    RPCResponse,
    RPCRequest
)


logger: logging.Logger = logging.getLogger(__name__)


def parse_rpc_object(obj: Dict[str, Any]) -> RPCData:
    """
    Attempts to parse a dictionary into a recognized RPC schema models.

    Args:
        obj (dict): The dictionary representing the JSON-RPC message.

    Returns:
        RPCData: A Pydantic model representing the parsed RPC object.

    Raises:
        ValueError: If the input object doesn't match any known schema.
    """

    if "method" in obj and "id" in obj:
        return RPCRequest(**obj)
    elif "method" in obj:
        return RPCNotification(**obj)
    elif "result" in obj or "error" in obj:
        return RPCResponse(**obj)
    else:
        raise ValueError(f"Unknown RPC object: {obj}")


def serialize_payload(obj: Union[BaseModel, list, dict]) -> Union[dict, list]:
    """
    Recursively converts a payload object or collection of objects into a
    JSON-serializable format.

    Args:
        obj (BaseModel | list | dict): The payload to serialize.

    Returns:
        dict | list: A dict or list that can be encoded to JSON.
    """

    if isinstance(obj, BaseModel):
        return obj.model_dump()
    elif isinstance(obj, list):
        return [serialize_payload(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: serialize_payload(v) for k, v in obj.items()}


def encode_payload(payload: RPCPayload) -> bytes:
    """
    Encodes a payload into a length-prefixed binary format.

    Args:
        payload (RPCPayload): The data to encode.

    Returns:
        bytes: The binary representation of the payload.
    """

    serialized: bytes = json.dumps(serialize_payload(payload)).encode("utf-8")
    return struct.pack(">I", len(serialized)) + serialized


async def decode_payload(
    reader: asyncio.StreamReader
) -> Optional[RPCPayload]:
    """
    Decodes a length-prefixed message from the TCP stream and parses it
    into an RPC model.

    Args:
        reader (asyncio.StreamReader): The stream reader to decode from.

    Returns:
        Optional[RPCPayload]: The parsed RPC object(s) or None on failure.

    Raises:
        asyncio.IncompleteReadError: If the stream ends unexpectedly.
        json.JSONDecodeError: If the message cannot be decoded from JSON.
        struct.error: If message length bytes are malformed.
    """

    try:
        length_bytes: bytes = await reader.readexactly(4)
        message_length: int = struct.unpack(">I", length_bytes)[0]

        raw_data: bytes = await reader.readexactly(message_length)
        decoded_json: Union[dict, list] = json.loads(raw_data.decode("utf-8"))

        if isinstance(decoded_json, dict):
            return parse_rpc_object(decoded_json)
        elif isinstance(decoded_json, list):
            return cast(RPCPayload, [
                parse_rpc_object(item)
                for item in decoded_json
                if isinstance(item, dict)
            ])

    except (json.JSONDecodeError, struct.error) as err:
        logger.error(f"[DECODE] Failed to decode message: {err}")
        return None
