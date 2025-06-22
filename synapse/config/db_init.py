"""
Initialize database and create all needed tables
"""

from .db_config import engine
from ..models.base_model import Base

def initialize_database():
    """
    Initialize database by creating all tables.
    """

    Base.metadata.create_all(bind=engine)
