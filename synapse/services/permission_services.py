import logging
from typing import List, Callable, Optional

from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import IntegrityError

from ..types.rpc_types import RPCAction
from ..models.application_model import Application
from ..models.application_permission_model import ApplicationPermission
from .application_services import find_application_by_id, find_applications


logger = logging.getLogger(__name__)

QueryMethod = Callable[
    [Query[ApplicationPermission]], Query[ApplicationPermission]
]


def find_permission_by_id(
    db: Session,
    permission_id: str
) -> Optional[ApplicationPermission]:
    """
    Find a specific permission by its ID.

    Args:
        db (Session): SQLAlchemy database session
        permission_id (str): The ID of the permission to retrieve

    Returns:
        Optional[ApplicationPermission]: The permission object if found,
        otherwise None
    """

    try:
        permission = db.query(ApplicationPermission).filter_by(
            id=permission_id
        ).first()

        if permission is None:
            logger.warning(
                f"[PERMISSION] No permission found with ID: '{permission_id}'"
            )

        return permission

    except Exception as err:
        logger.error(
            f"[PERMISSION] Failed to retrieve permission by ID: {err}"
        )
        return None


def find_permissions(
    db: Session,
    filter_fn: Optional[QueryMethod] = None,
    sort_fn: Optional[QueryMethod] = None,
    skip: int = 0,
    limit: int = 0
) -> List[ApplicationPermission]:
    """
    Find permissions using custom filter and sort functions.

    Args:
        db (Session): SQLAlchemy session.
        filter_fn (Optional[QueryMethod]): Function that applies filters to the
            query.
        sort_fn (Optional[QueryMethod]): Function that applies sorting to the
            query.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return (<= 0 for all).

    Returns:
        List[ApplicationPermission]: List of permissions.
    """

    try:
        query = db.query(ApplicationPermission)

        if filter_fn:
            query = filter_fn(query)

        if sort_fn:
            query = sort_fn(query)

        if skip > 0:
            query = query.offset(skip)

        if limit > 0:
            query = query.limit(limit)

        return query.all()

    except Exception as err:
        logger.error(f"[PERMISSION] Failed to list permissions: {err}")
        return []


def grant_permission(
    db: Session,
    owner_id: str,
    target_id: str,
    action: RPCAction
) -> Optional[ApplicationPermission]:
    """
    Create a new permission relationship.

    Args:
        db (Session): SQLAlchemy database session
        owner_id (str): The ID of the application granting the permission
        target_id (str): The ID of the application receiving the permission
        action (RPCAction): The action being permitted

    Returns:
        Optional[ApplicationPermission]: The created ApplicationPermission
            object or None if creation failed
    """

    if owner_id == target_id:
        logger.warning(
            f"[PERMISSION] Cannot grant permission to self: '{owner_id}'"
        )
        return None

    try:
        reverse_permission = db.query(ApplicationPermission).filter_by(
            owner_id=target_id,
            target_id=owner_id,
            action=action
        )

        if reverse_permission:
            logger.warning(
                f"[PERMISSION] Cannot grant permission, reverse permission "
                f"exists: '{target_id}' -> '{owner_id}' for action "
                f"'{action.value}'"
            )
            return None

        owner_app = find_application_by_id(db, owner_id)
        target_app = find_application_by_id(db, target_id)

        if not owner_app:
            logger.error(
                f"[PERMISSION] Owner application '{owner_id}' does not exist"
            )
            return None

        if not target_app:
            logger.error(
                f"[PERMISSION] Target application '{target_id}' does not exist"
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
            f"[PERMISSION] Granted permission: '{owner_id}' -> '{target_id}' "
            f"for action '{action.value}'"
        )
        return permission

    except ValueError as err:
        db.rollback()
        logger.warning(f"[PERMISSION] Validation error: {err}")
        return None
    except IntegrityError as err:
        db.rollback()
        logger.warning(
            f"[PERMISSION] Permission already exists or constraint violation: "
            f"{err}"
        )
        return None
    except Exception as err:
        db.rollback()
        logger.error(f"[PERMISSION] Failed to grant permission: {err}")
        return None


def revoke_permission(
    db: Session,
    permission_id: str
) -> bool:
    """
    Remove a specific permission by its ID.

    Args:
        db (Session): SQLAlchemy database session
        permission_id (str): The ID of the permission to revoke

    Returns:
        bool: True if revocation was successful, False otherwise
    """

    try:
        rows_deleted = db.query(ApplicationPermission).filter_by(
            id=permission_id
        ).delete()

        if rows_deleted == 0:
            logger.warning(
                f"[PERMISSION] No permission found to revoke with ID: "
                f"'{permission_id}'"
            )
            return False

        db.commit()
        logger.info(
            f"[PERMISSION] Revoked permission with ID: '{permission_id}'"
        )
        return True

    except Exception as err:
        db.rollback()
        logger.error(f"[PERMISSION] Failed to revoke permission: {err}")
        return False


def find_authorized_applications(
    db: Session,
    target_id: str,
    action: RPCAction,
    active_only: bool = True
) -> List[Application]:
    """
    Find all applications authorized to perform a specific action on a target.
    This includes both applications with explicit permissions and admin
    applications.

    Args:
        db (Session): SQLAlchemy database session
        target_id (str): The UUID of the target application
        action (RPCAction): The action to check authorization for
        active_only (bool): If True, only consider active permissions

    Returns:
        List[Application]: List of Application objects that are authorized
    """

    try:
        authorized_apps = set()

        def target_permission_filter(query):
            filtered_query = query.filter_by(
                target_id=target_id,
                action=action
            )

            if active_only:
                filtered_query = filtered_query.filter(
                    ApplicationPermission.is_active.is_(True)
                )

            return filtered_query

        target_permissions = find_permissions(
            db=db,
            filter_fn=target_permission_filter
        )

        for permission in target_permissions:
            owner_app = find_application_by_id(db, permission.owner_id)
            if owner_app:
                authorized_apps.add(owner_app)

        admin_apps = find_applications(
            db=db,
            filter_fn=lambda q: q.filter(Application.is_admin.is_(True))
        )

        authorized_apps.update(admin_apps)

        logger.debug(
            f"[PERMISSION] Found {len(authorized_apps)} authorized "
            f"applications for action '{action.value}' on target '{target_id}'"
        )

        return list(authorized_apps)

    except Exception as err:
        logger.error(
            f"[PERMISSION] Failed to find authorized applications for target "
            f"'{target_id}' and action '{action.value}': {err}"
        )
        return []
