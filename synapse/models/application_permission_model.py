import logging
from typing import Final, TYPE_CHECKING

from sqlalchemy import (
    Index,
    String,
    Integer,
    Boolean,
    ForeignKey,
    Enum as PgEnum,
    CheckConstraint,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, relationship, mapped_column

from .base_model import Base
from ..types.rpc_types import RPCAction

if TYPE_CHECKING:
    from .application_model import Application


logger: Final[logging.Logger] = logging.getLogger(__name__)


class ApplicationPermission(Base):
    """
    Stores the permissions an application has over others.
    Manages both direct application-to-application permissions
    and application-to-group permissions.
    """

    __tablename__ = "application_permissions"

    __table_args__ = (
        UniqueConstraint(
            "action",
            "owner_id",
            "target_id",
            name="unique_permission_per_action_and_target"
        ),
        CheckConstraint(
            "owner_id != target_id",
            name="no_self_permissions"
        ),
        Index("idx_target_lookup", "target_id", "is_active"),
        Index("idx_active_owner_action", "is_active", "owner_id", "action")
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    owner_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    target_id: Mapped[str] = mapped_column(
        String,
        index=True,
        nullable=False
    )
    action: Mapped[RPCAction] = mapped_column(
        PgEnum(RPCAction, name="rpc_action", native_enum=False),
        index=True,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        index=True,
        default=True,
        nullable=False
    )

    owner: Mapped["Application"] = relationship(
        "Application",
        foreign_keys="[ApplicationPermission.owner_id]",
        back_populates="owned_permissions"
    )
    target: Mapped["Application"] = relationship(
        "Application",
        foreign_keys="[ApplicationPermission.target_id]",
        back_populates="target_permissions"
    )


    def __repr__(self) -> str:
        """
        Represent permissions as a string
        """

        return (
            "<ApplicationPermission("
            f"id='{self.id}', "
            f"action='{self.action.value}', "
            f"owner='{self.owner_id}', "
            f"target='{self.target_id}', "
            f"active={self.is_active}"
            ")>"
        )


    def to_dict(self) -> dict:
        """
        Convert permission to dictionary representation

        Returns:
            dict: Dictionary representation of the application permission
        """

        return {
            "id": self.id,
            "action":  self.action.value,
            "owner_id": self.owner_id,
            "target_id": self.target_id,
            "is_active": self.is_active
        }
