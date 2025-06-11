"""
Emit JSON-RPC messages to TCP clients.

Provides a utility to broadcast encoded messages to a group of connected
TCP clients using asyncio stream writers.
"""

import asyncio
import logging
from typing import Set

from ..types.rpc_types import RPCPayload
from .payload_utils import encode_payload


logger: logging.Logger = logging.getLogger(__name__)


async def emit_message(
    payload: RPCPayload,
    writers: Set[asyncio.StreamWriter]
) -> None:
    """
    Broadcast a JSON-RPC payload to all connected writers.

    Args:
        payload (RPCPayload): The JSON-RPC message to send.
        writers (Set[asyncio.StreamWriter]): Set of active TCP stream writers.
    """

    encoded: bytes = encode_payload(payload)

    for writer in writers:
        name: str = writer.get_extra_info("peername")

        try:
            writer.write(encoded)
            await writer.drain()
            logger.debug(f"[EMIT] Sent payload to {name}")
        except Exception as err:
            logger.error(f"[EMIT] Failed to send payload to {name}: {err}")
