"""
Module entry point to configure project, load configurations/variables and run
the project.
"""

import ssl
import asyncio
import logging
from os import getenv

from dotenv import load_dotenv

from .peer import handle_peer
from .config.db_init import initialize_database


load_dotenv()

HOST: str = getenv("HOST", "localhost")
PORT: int = int(getenv("PORT", "8080"))

KEY_FILE: str = getenv("TLS_KEY", "certs/key.pem")
CERT_FILE: str = getenv("TLS_CERT", "certs/cert.pem")

DEBUG: bool = bool(getenv("DEBUG", True))
LOG_LEVEL: str = getenv("LOG_LEVEL", ("DEBUG" if DEBUG else "INFO")).upper()


if LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
    LOG_LEVEL: str = "INFO"

logger: logging.Logger = logging.getLogger(__name__)

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    level=getattr(logging, LOG_LEVEL)
)


async def main() -> None:
    """
    Starts the asynchronous SSL-enabled JSON-RPC server.

    The server listens on the configured host and port, handles incoming
    connections using the `handle_peer` function, and uses SSL certificates
    for secure communication.
    """

    initialize_database()

    context: ssl.SSLContext = ssl.create_default_context(
        ssl.Purpose.CLIENT_AUTH
    )

    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    server: asyncio.AbstractServer = await asyncio.start_server(
        client_connected_cb=handle_peer,
        ssl=context,
        host=HOST,
        port=PORT
    )

    for sock in server.sockets or []:
        logger.info(f"[BOOT] Synapse server running on {sock.getsockname()}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[BOOT] Server shutdown requested.")
    except Exception as err:
        logger.exception(f"[BOOT] Error during server startup: {err}")
