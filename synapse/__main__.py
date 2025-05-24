"""
Module entry point to configure project and load configurations and variables.
"""

import os
import logging
import asyncio
import uvicorn
import websockets
from fastapi import FastAPI
from dotenv import load_dotenv
from .socket.server import handle_connection
from .handlers.agent_handler import router as agent_router


load_dotenv()

HOST: str = os.getenv("HOST", "localhost")
SERVER_HOST: str = os.getenv("SERVER_HOST", HOST)
SOCKET_HOST: str = os.getenv("SOCKET_HOST", HOST)
SERVER_PORT: int = int(os.getenv("SERVER_PORT", "5050"))
SOCKET_PORT: int = int(os.getenv("SOCKET_PORT", "8765"))

DEBUG: bool = bool(os.getenv("DEBUG", "true"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", ("DEBUG" if DEBUG else "INFO")).upper()

if LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
    LOG_LEVEL = "INFO"

app = FastAPI()
logger = logging.getLogger(__name__)

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    level=getattr(logging, LOG_LEVEL)
)
app.include_router(agent_router, prefix="/api")

async def run_server(host: str, port: int, log_level: str) -> None:
    config = uvicorn.Config(app, host=host, port=port, log_level=log_level.lower())
    server = uvicorn.Server(config)
    logger.info(f"Synapse server running at http://{host}:{port}")
    await server.serve()

async def run_socket(host: str, port: int) -> None:
    server = await websockets.serve(handle_connection, host, port)
    logger.info(f"Synapse socket running at ws://{host}:{port}")
    await server.wait_closed()

async def main() -> None:
    await asyncio.gather(
        run_server(SERVER_HOST, SERVER_PORT, LOG_LEVEL),
        run_socket(SOCKET_HOST, SOCKET_PORT)
    )

if __name__ == "__main__":
    logger.info("Starting synapse servers...")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Servers shutting down.")
    except Exception as error:
        logger.exception(f"Unexpected error: {error}")
