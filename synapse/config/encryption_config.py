"""
Encryption configuration module. Loads Fernet encryption key from environment
variables.
"""

import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from typing import Final


load_dotenv()

FERNET_KEY: Final[str] = os.getenv("FERNET_KEY", "")

if not FERNET_KEY:
    raise ValueError("Missing FERNET_KEY in environment variables.")

cipher: Final[Fernet] = Fernet(FERNET_KEY)
