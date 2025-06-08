import base64
import logging
from typing import Final
from sqlalchemy import String
from sqlalchemy.orm import validates, DeclarativeBase, Mapped, mapped_column

from ..config.encryption_config import cipher


logger: Final[logging.Logger] = logging.getLogger(__name__)

class Application(DeclarativeBase):
    """
    Application model for PostgreSQL database.
    """

    __tablename__: str = "applications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    uri: Mapped[str] = mapped_column(String, nullable=False)
    authorization_token: Mapped[str | None] = mapped_column(
        String, nullable=True
    )


    def __repr__(self) -> str:
        """
        Express model self as a string
        """

        return f"<Application(id='{self.id}')>"


    @validates("authorization_toke")
    def _encrypt_token(self, _: str, value: str | None) -> str | None:
        """
        Encrypts the authorization token before storing it.
        """

        if value and not self._is_already_encrypted(value):
            encrypted_bytes: bytes = cipher.encrypt(value.encode("utf-8"))
            return base64.b64encode(encrypted_bytes).decode("utf-8")

        return value


    def _is_already_encrypted(self, value: str) -> bool:
        """
        Checks whether a given string is already encrypted.
        """

        try:
            encrypted_bytes: bytes = base64.b64decode(value)
            cipher.decrypt(encrypted_bytes)
            return True
        except Exception as err:
            logger.debug(f"[Model] Failed to assert token encrypted: {err}")
            return False


    @property
    def decrypted_api_key(self) -> str:
        """
        Decrypts and returns the authorization token.
        """

        if self.authorization_token:
            try:
                decoded_bytes: bytes = base64.b64decode(
                    self.authorization_token
                )
                return cipher.decrypt(decoded_bytes).decode("utf-8")
            except Exception as err:
                logger.debug(f"[Model] Failed to decrypt token: {err}")

        return ""
