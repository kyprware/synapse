import logging
from typing import List, Callable, Optional, Dict, Any

from sqlalchemy.orm import Session, Query

from ..models.application_model import Application


logger = logging.getLogger(__name__)

QueryMethod = Callable[[Query[Application]], Query[Application]]


def find_application_by_id(
    db: Session,
    app_id: str
) -> Optional[Application]:
    """
    Find an application by its ID.

    Args:
        db (Session): SQLAlchemy database session
        app_id (str): The ID of the application to retrieve

    Returns:
        Optional[Application]: The Application object or None if not found
    """

    try:
        return db.query(Application).filter_by(id=app_id).one_or_none()
    except Exception as err:
        logger.error(
            f"[APPLICATION] Failed to retrieve application '{app_id}': {err}"
        )
        return None


def find_applications(
    db: Session,
    filter_fn: Optional[QueryMethod] = None,
    sort_fn: Optional[QueryMethod] = None,
    skip: int = 0,
    limit: int = 0
) -> List[Application]:
    """
    Find all applications in the system with optional filtering and sorting.

    Args:
        db (Session): SQLAlchemy database session
        filter_fn (Optional[QueryMethod]): function to filter the query
        sort_fn (Optional[QueryMethod]): function to sort the query
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return (<= 0 for all).

    Returns:
        List[Application]: List of Application objects
    """

    try:
        query: Query[Application] = db.query(Application)

        if filter_fn is not None:
            query = filter_fn(query)

        if sort_fn is not None:
            query = sort_fn(query)

        if skip > 0:
            query = query.offset(skip)

        if limit > 0:
            query = query.limit(limit)

        return query.all()

    except Exception as err:
        logger.error(f"[APPLICATION] Failed to retrieve applications: {err}")
        return []


def create_application(
    db: Session,
    name: str,
    description: str,
    server_url: str,
    password: Optional[str] = None,
    is_admin: bool = False
) -> Optional[Application]:
    """
    Create a new application with URL and optional authentication token.

    Args:
        db (Session): SQLAlchemy database session
        name (str): Name of the application
        description (str): Description of the application and what it does
        server_url (str): The application's server URL
        password (Optional[str]): Optional password
        is_admin (bool): If the application has SYNAPSE admin permissions

    Returns:
        Optional[Application]: The created Application object or None if
            creation failed

    Raises:
        ValueError: If validation fails
    """

    if not name or not name.strip():
        logger.error("[APPLICATION] Application name cannot be empty")
        return None

    if not server_url or not server_url.strip():
        logger.error("[APPLICATION] Server URL cannot be empty")
        return None

    try:
        app = Application(
            name=name.strip(),
            description=description.strip() if description else "",
            server_url=server_url.strip(),
            password=password.strip() if password else None,
            is_admin=is_admin
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        logger.info(f"[APPLICATION] Created application with ID: {app.id}")
        return app
    except Exception as err:
        db.rollback()
        logger.error(f"[APPLICATION] Failed to create application: {err}")
        return None


def update_application(
    db: Session,
    app_id: str,
    updates: Dict[str, Any]
) -> Optional[Application]:
    """
    Update application fields using the model's update_from_dict method.

    Args:
        db (Session): SQLAlchemy database session
        app_id (str): The ID of the application to update
        updates (Dict[str, Any]): Dictionary of fields to update

    Returns:
        Optional[Application]: The updated Application object or None if update
            failed
    """

    if not updates:
        logger.warning(
            f"[APPLICATION] No updates provided for application '{app_id}'"
        )
        return None

    try:
        app = db.query(Application).filter_by(id=app_id).first()

        if not app:
            logger.warning(
                f"[APPLICATION] No application found with ID '{app_id}'"
            )
            return None

        if 'name' in updates and updates['name']:
            updates['name'] = updates['name'].strip()
        if 'description' in updates and updates['description']:
            updates['description'] = updates['description'].strip()
        if 'server_url' in updates and updates['server_url']:
            updates['server_url'] = updates['server_url'].strip()
        if 'auth_token' in updates and updates['auth_token']:
            updates['auth_token'] = updates['auth_token'].strip()

        app.update_from_dict(updates)

        db.commit()
        db.refresh(app)

        logger.info(f"[APPLICATION] Updated application '{app_id}'")
        return app

    except Exception as err:
        db.rollback()
        logger.error(
            f"[APPLICATION] Failed to update application '{app_id}': {err}"
        )
        return None


def delete_application(db: Session, app_id: str) -> bool:
    """
    Permanently remove an application and all its permissions.

    Args:
        db (Session): SQLAlchemy database session
        app_id (str): The ID of the application to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """

    try:
        app = db.query(Application).filter_by(id=app_id).first()

        if not app:
            logger.warning(
                f"[APPLICATION] Application '{app_id}' not found for deletion"
            )
            return False

        db.delete(app)
        db.commit()
        logger.info(f"[APPLICATION] Deleted application '{app_id}'")
        return True
    except Exception as err:
        db.rollback()
        logger.error(
            f"[APPLICATION] Failed to delete application '{app_id}': {err}"
        )
        return False
