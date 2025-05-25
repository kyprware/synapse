import base64
import logging
from redis_om import HashModel

from ..config.db_config import redis
from ..config.encryption_config import cipher


logger = logging.getLogger(__name__)

class AgentModel(HashModel):
    uuid: str
    api_key: str
    ping_url: str

    class Meta:
        database = redis

    def __setattr__(self, name, value):
        if name == "api_key" and value and not self._is_already_encrypted(value):
            encrypted_bytes = cipher.encrypt(value.encode('utf-8'))
            value = base64.b64encode(encrypted_bytes).decode("utf-8")

        super().__setattr__(name, value)

    @classmethod
    def _is_already_encrypted(cls, value: str) -> bool:
        try:
            encrypted_bytes = base64.b64decode(value)
            cipher.decrypt(encrypted_bytes)
            return True
        except Exception as error:
            logger.debug(f"[Model] Failed to assert api key ecrypted: {error}")
            return False

    @property
    def decrypted_api_key(self) -> str:
        if self.api_key:
            try:
                decoded_bytes = base64.b64decode(self.api_key)
                decrypted_bytes = cipher.decrypt(decoded_bytes)
                return decrypted_bytes.decode("utf-8")
            except Exception as error:
                logger.debug(f"[Model] Failed to decrypt api key: {error}")
        return ""
