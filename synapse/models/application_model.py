import uuid
import base64
import logging

from typing import Final, Optional

from sqlalchemy import (
    String,
    Boolean,
)
from sqlalchemy.orm import (
    Mapped,
    validates,
    relationship,
    mapped_column
)

from .base_model import Base
from ..config.encryption_config import cipher
from ..utils.validator_utils import validate_url


logger: Final[logging.Logger] = logging.getLogger(__name__)


class Application(Base):
    """
    Application model for PostgreSQL database.
    """

    __tablename__: str = "applications"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    url: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    authentication_token: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    owned_permissions = relationship(
        "ApplicationPermission",
        back_populates="owner",
        foreign_keys="[ApplicationPermission.owner_id]",
        cascade="all, delete-orphan"
    )
    targeted_by_permissions = relationship(
        "ApplicationPermission",
        back_populates="target",
        foreign_keys="[ApplicationPermission.target_id]",
        cascade="all, delete-orphan"
    )


    def __repr__(self) -> str:
        """
        String representation of model object
        """

        return f"<Application(id='{self.id}')>"


    @validates("url")
    def validate_url_field(self, key: str, value: str) -> str:
        """
        Validate application url
        """

        return validate_url(key, value)


    @validates("authentication_token")
    def encrypt_token(self, _: str, value: Optional[str]) -> Optional[str]:
        """
        Encrypts the authentication token before storing it.
        """

        if value and not self._is_already_encrypted(value):
            try:
                encrypted_bytes: bytes = cipher.encrypt(value.encode("utf-8"))
                return base64.b64encode(encrypted_bytes).decode("utf-8")
            except Exception as err:
                logger.debug(f"[Model] Encryption failed: {err}")

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
        Decrypts and returns the authentication token.
        """

        if self.authentication_token:
            try:
                decoded_bytes: bytes = base64.b64decode(
                    self.authentication_token
                )
                return cipher.decrypt(decoded_bytes).decode("utf-8")
            except Exception as err:
                logger.debug(f"[Model] Failed to decrypt token: {err}")

        return ""


    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "url": self.url,
            "description": self.description,
            "is_active": self.is_active,
        }
