"""
Module entry point to configure project, load configurations/variables and run
the project.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

HOST: str = os.getenv("HOST", "localhost")
DEBUG: bool = bool(os.getenv("DEBUG", "true"))
SERVER_HOST: str = os.getenv("SERVER_HOST", HOST)
SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8080"))

LOG_LEVEL: str = os.getenv("LOG_LEVEL", ("DEBUG" if DEBUG else "INFO")).upper()

if LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
    LOG_LEVEL: str = "INFO"

logger = logging.getLogger(__name__)

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    level=getattr(logging, LOG_LEVEL)
)

if __name__ == "__main__":
    logger.info("Starting synapse servers...")
