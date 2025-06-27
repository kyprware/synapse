"""
Asynchronous JSON-RPC TCP handler module.

Handles incoming JSON-RPC requests, notifications, and responses over a
TCP stream using asyncio streams.
"""

import asyncio
import logging
from typing import Optional, Tuple, List, Set, cast


from .utils.emit_utils import emit_message
from .config.db_config import SessionLocal
from .config.dispatch_config import dispatcher
from .utils.dispatch_utils import dispatch_rpc
from .utils.payload_utils import decode_payload
from .types.rpc_types import RPCBatchData, RPCPayload, RPCAction
from .services.permission_services import find_authorized_applications
from .schemas.application_connection_schema import ApplicationConnection
from .services.connection_services import (
    find_connections,
    remove_connection,
    find_connection_by_writer
)
from .schemas.rpc_schema import (
    RPCNotification,
    RPCResponse,
    RPCRequest,
    RPCError
)


logger: logging.Logger = logging.getLogger(__name__)


def find_authorized_writers(
    target_id: Optional[str],
    action: RPCAction,
) -> Set[asyncio.StreamWriter]:
    """
    Find writers authorized to perform an action on a target.

    Args:
        target_id (Optional[str]): The target application ID
        action (RPCAction): The RPC action to check authorization for

    Returns:
        Set[asyncio.StreamWriter]: Set of authorized writers
    """

    authorized_writers: Set[asyncio.StreamWriter] = set()

    with SessionLocal() as db:
        authorized_app_ids = {
            app.id
            for app in find_authorized_applications(db, target_id, action)
        }

        for connection in find_connections():
            if connection.id in authorized_app_ids:
                authorized_writers.add(connection.writer)

    return authorized_writers


async def handle_spokes(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> None:
    """
    Handles an individual JSON-RPC session with a connected application.

    Reads payload from the TCP stream, determines its type
    (notification, request, or response), and dispatches and broadcasts
    accordingly.

    Args:
        reader (asyncio.StreamReader): The stream reader for the connection.
        writer (asyncio.StreamWriter): The stream writer for the connection.
    """

    spoke: Optional[Tuple[str, int]] = writer.get_extra_info("peername")
    logger.info(f"[CONNECTION] Connection from {spoke}")

    try:
        initial_payload: Optional[RPCPayload] = await decode_payload(reader)

        if not isinstance(initial_payload, RPCRequest):
            logger.error(
                "[CONNECTION] Rejected: Initial payload was not an RPCRequest"
            )
            return None

        if initial_payload.method not in ["connect", "register"]:
            logger.error(
                "[CONNECTION] Rejected: invalid request method"
            )
            return None

        init_response: RPCResponse = await dispatch_rpc(
            dispatcher,
            cast(RPCRequest, initial_payload)
        )

        await emit_message(
            cast(RPCPayload, init_response),
            find_authorized_writers(
                target_id=None,
                action=RPCAction.OUTBOUND_RESPONSE
            )
        )

        if init_response.error:
            logger.error(
                f"[CONNECTION] Initialization failed: {init_response.error}"
            )
            return None


        connection: Optional[
            ApplicationConnection
        ] = find_connection_by_writer(writer)

        if not connection:
            logger.warning(
                f"[CONNECTION] Spoke {spoke} is not registered in connections"
            )
            return None

        while True:
            payload: Optional[RPCPayload] = await decode_payload(reader)

            batch_payload: RPCBatchData = cast(RPCBatchData,
                [payload] if not isinstance(payload, list) else payload
            )

            if all(isinstance(p, RPCResponse) for p in batch_payload):
                await emit_message((
                    batch_payload
                    if len(batch_payload) > 1 else batch_payload[0]
                ), find_authorized_writers(
                    target_id=connection.id,
                    action=RPCAction.OUTBOUND_RESPONSE
                ))
            elif all(isinstance(p, RPCNotification) for p in batch_payload):
                batch_response: List[RPCResponse] =  []

                await emit_message((
                    batch_payload
                    if len(batch_payload) > 1 else batch_payload[0]
                ), find_authorized_writers(
                    target_id=connection.id,
                    action=RPCAction.OUTBOUND_RESPONSE
                ))

                for payload in batch_payload:
                    response: RPCResponse = await dispatch_rpc(
                        dispatcher,
                        cast(RPCRequest, payload)
                    )

                    if isinstance(payload, RPCRequest):
                        batch_response.append(response)

                await emit_message(cast(RPCPayload,
                    batch_response
                    if len(batch_response) > 1 else batch_response[0]
                ), find_authorized_writers(
                    target_id=connection.id,
                    action=RPCAction.INBOUND_RESPONSE
                ))
            else:
                await emit_message(RPCResponse(
                    id=None,
                    error=RPCError(
                        code=-32603,
                        message=f"Invalid Request(s): {batch_payload}"
                    )
                ), find_authorized_writers(
                    target_id=connection.id,
                    action=RPCAction.INBOUND_RESPONSE
                ))

    except asyncio.IncompleteReadError as err:
        logger.error(f"[CONNECTION] {spoke} disconnected unexpectedly: {err}")
    except Exception as err:
        logger.exception(f"[CONNECTION] Unexpected error from {spoke}: {err}")
    finally:
        connection: Optional[
            ApplicationConnection
        ] = find_connection_by_writer(writer)

        if connection:
            remove_connection(connection)
            logger.info(f"[CONNECTION] spoke {spoke} disconnected")
