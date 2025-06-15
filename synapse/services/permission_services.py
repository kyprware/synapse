import logging

from typing import List, Callable, Optional

from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import IntegrityError

from ..types.rpc_types import RPCAction
from .application_services import get_application_by_id
from ..models.application_model import ApplicationPermission


logger = logging.getLogger(__name__)

PermissionQueryMethod = Callable[
    [Query[ApplicationPermission]], Query[ApplicationPermission]
]


def get_permissions_for_owner(
    db: Session,
    owner_id: str,
    active_only: bool = True
) -> List[ApplicationPermission]:
    """
    Get all permissions this application has been granted over others.

    Args:
        db (Session): SQLAlchemy database session
        owner_id (str): The UUID of the application that owns the permissions
        active_only (bool): If True, only return active permissions

    Returns:
        List[ApplicationPermission]: List of ApplicationPermission objects
            where this app is the owner
    """

    try:
        query = db.query(ApplicationPermission).filter_by(owner_id=owner_id)

        if active_only:
            query = query.filter(ApplicationPermission.is_active == True)

        return query.all()
    except Exception as err:
        logger.error(
            f"[PERMISSION] Failed to get permissions for owner"
            f"'{owner_id}': {err}"
        )
        return []


def get_permissions_for_target(
    db: Session,
    target_id: str,
    active_only: bool = True
) -> List[ApplicationPermission]:
    """
    Get all permissions that affect this application.

    Args:
        db (Session): SQLAlchemy database session
        target_id (str): The UUID of the application that is the target
        active_only (bool): If True, only return active permissions

    Returns:
        List[ApplicationPermission]: List of ApplicationPermission objects
            where this app is the target
    """

    try:
        query = db.query(ApplicationPermission).filter_by(target_id=target_id)

        if active_only:
            query = query.filter(ApplicationPermission.is_active == True)

        return query.all()
    except Exception as err:
        logger.error(
            f"[PERMISSION] Failed to get permissions for target"
            f"'{target_id}': {err}"
        )
        return []


def grant_permission(
    db: Session,
    owner_id: str,
    target_id: str,
    action: RPCAction
) -> Optional[ApplicationPermission]:
    """
    Create a new permission relationship with cyclical prevention.
    Prevents self-permissions and reverse permissions for the same action.

    Args:
        db (Session): SQLAlchemy database session
        owner_id (str): The UUID of the application granting the permission
        target_id (str): The UUID of the application receiving the permission
        action (RPCAction): The action being permitted

    Returns:
        Optional[ApplicationPermission]: The created ApplicationPermission
            object or None if creation failed
    """

    try:
        if owner_id == target_id:
            logger.warning(
                f"[PERMISSION] Cannot grant self-permission for application"
                f"'{owner_id}'"
            )
            return None

        reverse_permission = db.query(ApplicationPermission).filter_by(
            owner_id=target_id,
            target_id=owner_id,
            action=action,
            is_active=True
        ).first()

        if reverse_permission:
            logger.warning(
                f"[PERMISSION] Cannot grant permission - reverse permission"
                f"exists: '{target_id}' -> '{owner_id}' for action '{action}'"
            )
            return None

        if (
                not get_application_by_id(db, owner_id) or
                not get_application_by_id(db, target_id)
            ):
            logger.error(
                f"[PERMISSION] One or both applications do not exist:"
                f"'{owner_id}', '{target_id}'"
            )
            return None

        permission = ApplicationPermission(
            owner_id=owner_id,
            target_id=target_id,
            action=action
        )

        db.add(permission)
        db.commit()
        db.refresh(permission)

        logger.info(
            f"[PERMISSION] Granted permission: '{owner_id}' -> '{target_id}'"
            f"for action '{action}'"
        )
        return permission

    except IntegrityError as err:
        db.rollback()
        logger.warning(
            f"[PERMISSION] Permission already exists or constraint violation:"
            f"{err}"
        )
        return None
    except Exception as err:
        db.rollback()
        logger.error(f"[PERMISSION] Failed to grant permission: {err}")
        return None


def revoke_permission(
    db: Session,
    owner_id: str,
    target_id: str,
    action: RPCAction
) -> bool:
    """
    Remove a specific permission relationship.

    Args:
        db (Session): SQLAlchemy database session
        owner_id (str): The UUID of the application that owns the permission
        target_id (str): The UUID of the application that is the target
        action (RPCAction): The specific action to revoke

    Returns:
        bool: True if revocation was successful, False otherwise
    """

    try:
        rows_deleted = db.query(ApplicationPermission).filter_by(
            owner_id=owner_id,
            target_id=target_id,
            action=action
        ).delete()

        if rows_deleted == 0:
            logger.warning(
                f"[PERMISSION] No permission found to revoke: "
                f"'{owner_id}' -> '{target_id}' for action '{action}'"
            )
            return False

        db.commit()
        logger.info(
            f"[PERMISSION] Revoked permission: '{owner_id}' -> '{target_id}'"
            f"for action '{action}'"
        )
        return True

    except Exception as err:
        db.rollback()
        logger.error(f"[PERMISSION] Failed to revoke permission: {err}")
        return False


def check_has_permission(
    db: Session,
    owner_id: str,
    target_id: str,
    action: RPCAction,
    active_only: bool = True
) -> bool:
    """
    Validate if a permission exists between applications for a specific action.

    Args:
        db (Session): SQLAlchemy database session
        owner_id (str): The UUID of the application that should own the permission
        target_id (str): The UUID of the application that should be the target
        action (str): The action to check for
        active_only (bool): If True, only check active permissions

    Returns:
        bool: True if the permission exists, False otherwise
    """

    try:
        query = db.query(ApplicationPermission).filter_by(
            owner_id=owner_id,
            target_id=target_id,
            action=action
        )

        if active_only:
            query = query.filter(ApplicationPermission.is_active == True)

        return query.first() is not None

    except Exception as err:
        logger.error(f"[PERMISSION] Failed to check permission: {err}")
        return False
