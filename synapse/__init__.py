"""
Initialize application
"""

from .config.db_config import engine
from .models.base_model import Base

Base.metadata.create_all(bind=engine)
