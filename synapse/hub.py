"""
Asynchronous JSON-RPC TCP handler module.

Handles incoming JSON-RPC requests, notifications, and responses over a
TCP stream using asyncio streams.
"""

import asyncio
import logging
from typing import Optional, Tuple, List, cast


from .utils.emit_utils import emit_message
from .config.db_config import SessionLocal
from .config.dispatch_config import dispatcher
from .utils.payload_utils import decode_payload
from .utils.dispatch_utils import dispatch_rpcs
from .types.rpc_types import RPCAction, RPCBatchData, RPCPayload
from .utils.connection_utils import ConnectedApplicationRegistry
from .schemas.application_connection_shema import ConnectedApplication
from .services.permission_services import find_authorized_applications
from .schemas.rpc_schema import (
    RPCNotification,
    RPCResponse,
    RPCRequest,
    RPCError
)


logger: logging.Logger = logging.getLogger(__name__)
connected_applications: ConnectedApplication = ConnectedApplicationRegistry()


def get_authorized_writers() -> set[asyncio.StreamWriter]:
    return


async def handle_spokes(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> None:
    """
    Handles an individual JSON-RPC session with a connected application.

    Reads a single payload from the TCP stream, determines its type
    (notification, request, or response), and dispatches or broadcasts
    accordingly.

    Args:
        reader (asyncio.StreamReader): The stream reader for the connection.
        writer (asyncio.StreamWriter): The stream writer for the connection.
    """

    spoke: Optional[Tuple[str, int]] = writer.get_extra_info("peername")
    logger.info(f"[CONNECTION] Connection from {spoke}")

    try:
        initial_payload: Optional[RPCPayload] = await decode_payload(reader)

        if not initial_payload:
            return None

        if isinstance(initial_payload, RPCRequest):
            await emit_message(initial_payload, get_authorized_writers())

            response: List[RPCResponse] = await dispatch_rpcs(
                dispatcher,
                cast(RPCRequest, initial_payload)
            )

            await emit_message(
                cast(RPCPayload, response),
                get_authorized_writers()
            )
        else:
            logger.info("")

        while True:
            payload: Optional[RPCPayload] = await decode_payload(reader)

            if not payload:
                continue

            if isinstance(payload, RPCNotification):
                await emit_message(payload, get_authorized_writers())
            else:
                batch_payload: RPCBatchData = cast(RPCBatchData,
                    [payload] if not isinstance(payload, list) else payload
                )

                if all(isinstance(p, RPCResponse) for p in batch_payload):
                    await emit_message((
                        batch_payload
                        if len(batch_payload) > 1 else batch_payload[0]
                    ), get_authorized_writers())
                elif all(isinstance(p, RPCRequest) for p in batch_payload):
                    await emit_message((
                            batch_payload
                            if len(batch_payload) > 1 else batch_payload[0]
                        ), get_authorized_writers())

                    response: List[RPCResponse] = await dispatch_rpcs(
                        dispatcher,
                        *cast(List[RPCRequest], batch_payload)
                    )

                    await emit_message(cast(RPCPayload,
                        response if len(response) > 1 else response[0]
                    ), get_authorized_writers())
                else:
                    await emit_message(RPCResponse(
                        id=None,
                        error=RPCError(
                            code=-32603,
                            message=f"Invalid Request(s): {batch_payload}"
                        )
                    ), get_authorized_writers())

    except asyncio.IncompleteReadError as err:
        logger.error(f"[CONNECTION] {spoke} disconnected unexpectedly: {err}")
    except Exception as err:
        logger.exception(f"[CONNECTION] Unexpected error from {spoke}: {err}")
