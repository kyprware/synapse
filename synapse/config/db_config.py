"""
PostgreSQL database connection configuration using a DATABASE_URL.
"""

import os
from typing import Final
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session


load_dotenv()

DATABASE_URL: Final[str] = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/dbname"
)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required.")

engine: Final[Engine] = create_engine(DATABASE_URL, echo=False, future=True)

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)
