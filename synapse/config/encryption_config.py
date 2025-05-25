import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet


load_dotenv()

cipher = Fernet(os.getenv("FERNET_KEY", ""))
