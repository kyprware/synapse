import os
from dotenv import load_dotenv
from redis_om import get_redis_connection


load_dotenv()

HOST: str = os.getenv("HOST", "localhost")
REDIS_HOST: str = os.getenv("REDIS_HOST", HOST)
REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

redis = get_redis_connection(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)
