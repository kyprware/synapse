"""
Handles data streaming between LLM and agent services through websockets.
"""

import json
import logging
import websockets
from typing import Any
from websockets.legacy.server import WebSocketServerProtocol

from ..services import agent_service


logger = logging.getLogger(__name__)
connected_clients: dict[str, WebSocketServerProtocol] = {}

async def handle_connection(websocket: WebSocketServerProtocol) -> None:
    client_uuid: str = ""
    logger.info(f"[Socket] Client {websocket.remote_address} connected, awaiting agent information...")

    try:
        raw_client_info = await websocket.recv()
        logger.debug(f"[Socket] Client {websocket.remote_address} information recieved: {raw_client_info}")

        try:
            client_info: dict[str, Any] = json.loads(raw_client_info)
            client_uuid = client_info.get("uuid", "")

            agent = agent_service.get_agents(
                        filter_fn=lambda agent: agent.uuid == client_uuid
                    )[0]

            if not agent:
                raise ValueError("Client not found in agent record")

        except (json.JSONDecodeError, ValueError) as error:
            await websocket.send(f"Verification failed: {str(error)}")
            logger.warning(f"[Socket] Client failed verification: {error}")
            return

        connected_clients[client_uuid] = websocket
        await websocket.send("Verification successful.")
        logger.info(f"[Socket] Client {websocket.remote_address} verified with UUID {client_uuid}")

        async for message in websocket:
            logger.debug(f"[Socket] Received from {websocket.remote_address}: {message}")

    except websockets.exceptions.ConnectionClosed:
        logger.info(f"[Socket] Client {websocket.remote_address} disconnected")

    finally:
        if "client_uuid" in locals() and client_uuid in connected_clients:
            del connected_clients[client_uuid]
            logger.debug(f"[Socket] Client {client_uuid} removed from connected clients.")
