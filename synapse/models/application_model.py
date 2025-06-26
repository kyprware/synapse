import uuid
import base64
import logging

from typing import Final, Optional, TYPE_CHECKING

from sqlalchemy import Index, String, Boolean
from sqlalchemy.orm import Mapped, validates, relationship, mapped_column

from .base_model import Base
from ..config.encryption_config import cipher
from ..utils.validator_utils import validate_url

if TYPE_CHECKING:
    from .application_permission_model import ApplicationPermission


logger: Final[logging.Logger] = logging.getLogger(__name__)


class Application(Base):
    """
    Application model for PostgreSQL database.
    """

    __tablename__: str = "applications"

    __table_args__ = (
        Index("idx_active_admin", "is_active", "is_admin")
    )

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    server_url: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True
    )
    auth_token: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        index=True,
        default=False,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        index=True,
        default=True,
        nullable=False
    )

    owned_permissions: Mapped[list["ApplicationPermission"]] = relationship(
        "ApplicationPermission",
        back_populates="owner",
        foreign_keys="[ApplicationPermission.owner_id]",
        cascade="all, delete-orphan"
    )
    targeted_by_permissions: Mapped[
        list["ApplicationPermission"]
    ] = relationship(
        "ApplicationPermission",
        back_populates="target",
        foreign_keys="[ApplicationPermission.target_id]",
        cascade="all, delete-orphan"
    )


    def __repr__(self) -> str:
        """
        String representation of model object
        """

        return (
            "<Application("
            f"id='{self.id}' "
            f"name='{self.name}' "
            f"is_admin={self.is_admin} "
            f"is_active={self.is_active}"
            ")>"
        )


    @validates("server_url")
    def validate_url_field(self, key: str, value: str) -> str:
        """
        Validate application server url
        """

        return validate_url(key, value)


    @validates("auth_token")
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
                raise ValueError(
                    f"Failed to encrypt authentication token: {err}"
                )

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
            raise ValueError(f"Failed to assert if token is encrypted: {err}")

        return False


    @property
    def decrypted_auth_token(self) -> Optional[str]:
        """
        Decrypts and returns the authentication token.
        """

        if self.auth_token:
            try:
                decoded_bytes: bytes = base64.b64decode(self.auth_token)
                return cipher.decrypt(decoded_bytes).decode("utf-8")
            except Exception as err:
                logger.error(
                    f"[Model] Failed to decrypt token for app {self.id}: {err}"
                )

        return None


    def to_dict(self, include_auth_token: bool = False) -> dict:
        """
        Convert application to dictionary representation.

        Args:
            include_token (bool): Whether to include the decrypted token

        Returns:
            dict: Dictionary representation of the application
        """

        result = {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "server_url": self.server_url,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
        }

        if include_auth_token:
            result["auth_token"] = self.decrypted_auth_token

        return result


    def update_from_dict(self, data: dict) -> None:
        """
        Update application from dictionary data.

        Args:
            data (dict): Dictionary containing fields to update
        """

        allowed_fields = {
            "name",
            "description",
            "server_url",
            "auth_token",
            "is_admin",
            "is_active"
        }

        for field, value in data.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
