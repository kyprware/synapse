"""
Handles data streaming between LLM and agent services through websockets.
"""

import logging
import websockets


logger = logging.getLogger(__name__)

async def handle_connection(websocket) -> None:
    logger.info("Client connected")

    try:
        async for message in websocket:
            await websocket.send(message)
            logger.debug(f"Received: {message}")
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")
