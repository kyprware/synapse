"""
Application model module for SQLAlchemy ORM.
"""

import bcrypt
import logging
from typing import Final, Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, validates, mapped_column, relationship

from .base_model import Base
from ..utils.validator_utils import validate_url

if TYPE_CHECKING:
    from .application_permission_model import ApplicationPermission


logger: Final[logging.Logger] = logging.getLogger(__name__)


class Application(Base):
    """
    Application model for PostgreSQL database.
    """

    __tablename__: str = "applications"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
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
    _password_hash: Mapped[Optional[str]] = mapped_column(
        "password_hash",
        String,
        nullable=True
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
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


    @property
    def password(self) -> None:
        """
        Password is write-only.
        """

        raise AttributeError("Password is not readable")


    @password.setter
    def password(self, password: str) -> None:
        """
        Auto-hash password when set.

        Args:
            password (str): Plain text password to hash
        """

        if password:
            salt = bcrypt.gensalt()

            self._password_hash = bcrypt.hashpw(
                password.encode("utf-8"),
                salt
            ).decode("utf-8")
        else:
            self._password_hash = None


    def verify_password(self, password: str) -> bool:
        """
        Verify password against stored hash.

        Args:
            password (str): Password to verify

        Returns:
            bool: True if password matches, False otherwise
        """

        if not self._password_hash:
            return not password

        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                self._password_hash.encode("utf-8")
            )
        except Exception as err:
            logger.error(f"Password verification failed for application {err}")
            return False


    @validates("server_url")
    def validate_url_field(self, key: str, value: str) -> str:
        """
        Validate application server URL field.

        Args:
            key (str): The field name being validated.
            value (str): The URL value to validate.

        Returns:
            str: The validated URL value.
        """

        return validate_url(key, value)


    def to_dict(self) -> dict:
        """
        Convert application to dictionary representation.

        Returns:
            dict: Dictionary representation of the application.
        """

        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "server_url": self.server_url,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
        }


    def update_from_dict(self, data: dict) -> None:
        """
        Update application from dictionary data.

        Args:
            data (dict): Dictionary containing field names as keys and values.
        """

        for field, value in data.items():
            if field == "password" and value:
                self.password = value
            elif field in {
                "name",
                "description", 
                "server_url",
                "is_admin",
                "is_active"
            } and hasattr(self, field):
                setattr(self, field, value)


    def __repr__(self) -> str:
        """
        String representation of Application model.

        Returns:
            str: String representation of the application instance.
        """

        return (
            f"<Application("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"is_admin={self.is_admin}, "
            f"is_active={self.is_active}"
            f")>"
        )
