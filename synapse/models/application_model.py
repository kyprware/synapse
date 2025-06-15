import uuid
import base64
import logging

from typing import Final, Optional

from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    Enum as PgEnum,
    UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped,
    validates,
    relationship,
    mapped_column,
    DeclarativeBase,
)

from ..types.rpc_types import RPCAction
from ..config.encryption_config import cipher
from ..utils.validator_utils import validate_url, validate_uuid


logger: Final[logging.Logger] = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


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


class ApplicationPermission(Base):
    """
    Stores the permissions an application has over others.
    """

    __tablename__ = "application_permissions"

    __table_args__ = (
        UniqueConstraint(
            "action",
            "owner_id",
            "target_id",
            name="unique_permission_per_action"
        ),
    )

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    owner_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    action: Mapped[RPCAction] = mapped_column(
        PgEnum(RPCAction, name="rpc_action", native_enum=False),
        nullable=False
    )

    owner = relationship(
        "Application",
        foreign_keys="[ApplicationPermission.owner_id]",
        back_populates="owned_permissions"
    )
    target = relationship(
        "Application",
        foreign_keys="[ApplicationPermission.target_id]",
        back_populates="targeted_by_permissions"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )


    def __repr__(self) -> str:
        """
        Represent permissions as a string
        """

        return (
            "<ApplicationPermission("
                f"action='{self.action}', "
                f"owner='{self.owner_id}', "
                f"target='{self.target_id}'"
            ">"
        )


    @validates("owner_id", "target_id")
    def validate_uuid_fields(self, key: str, value: str) -> str:
        """
        Validate application uuids
        """

        return validate_uuid(key, value)


    @validates("action")
    def validate_action(self, _: str, value) -> RPCAction:
        """
        Validate that the action is a valid RPCAction enum value
        """

        if isinstance(value, str):
            try:
                return RPCAction(value)
            except ValueError:
                raise ValueError(
                    f"Invalid action: {value}. Must be of {list(RPCAction)}"
                )
        elif isinstance(value, RPCAction):
            return value
        else:
            raise ValueError(
                f"Action must be a string or RPCAction enum, got {type(value)}"
            )


    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "owner_id": self.owner_id,
            "target_id": self.target_id,
            "action": (
                self.action.value
                if isinstance(self.action, RPCAction) else
                self.action,
            ),
            "is_active": self.is_active,
        }
