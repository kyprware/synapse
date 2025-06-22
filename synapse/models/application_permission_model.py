import uuid
import logging

from typing import Final

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
    mapped_column
)

from .base_model import Base
from ..types.rpc_types import RPCAction
from ..utils.validator_utils import validate_uuid


logger: Final[logging.Logger] = logging.getLogger(__name__)


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
