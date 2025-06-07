"""
PostgreSQL database connection configuration. Loads connection parameters from
environment variables and creates an SQLAlchemy engine.
"""

import os
from typing import Final
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


load_dotenv()

DB_USER: Final[str] = os.getenv("POSTGRES_USER", "")
DB_PASSWORD: Final[str] = os.getenv("POSTGRES_PASSWORD", "")
DB_HOST: Final[str] = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT: Final[str] = os.getenv("POSTGRES_PORT", "5432")
DB_NAME: Final[str] = os.getenv("POSTGRES_DB", "")

if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("Missing required PostgreSQL environment variables.")

DATABASE_URL: Final[str] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine: Final[Engine] = create_engine(DATABASE_URL, echo=False, future=True)
