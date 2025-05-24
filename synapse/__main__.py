"""
Module entry point to configure project and load configurations and variables.
"""

import os
import logging
import asyncio
from dotenv import load_dotenv
from .socket.server import run as start_socket


load_dotenv()

HOST: str = os.getenv("HOST", "localhost")
PORT: int = int(os.getenv("PORT", "8765"))

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        level=logging.INFO
    )

    logger.info("Starting Synapse WebSocket server...")

    try:
        asyncio.run(start_socket(HOST, PORT))
    except KeyboardInterrupt:
        logger.info("Socket server shutting down.")
    except Exception as error:
        logger.exception(f"Unexpected error: {error}")
