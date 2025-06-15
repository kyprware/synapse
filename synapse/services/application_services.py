import logging

from typing import List, Callable, Optional, Dict, Any

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, Query

from ..models.application_model import Application


logger = logging.getLogger(__name__)

QueryMethod = Callable[
    [Query[Application]], Query[Application]
]


def create_application(
    db: Session,
    url: str,
    description: str,
    authentication_token: Optional[str] = None
) -> Optional[Application]:
    """
    Create a new application with URL and optional authentication token.

    Args:
        db (Session): SQLAlchemy database session
        url (str): The application's URL (must be valid)
        description (str): Optional description of the application
        authentication_token Optional[str]: Optional authentication token

    Returns:
        Optional[Application]: The created Application object or None if
            creation failed

    Raises:
        ValueError: If URL validation fails
    """

    try:
        app = Application(
            url=url,
            description=description,
            authentication_token=authentication_token
        )
        db.add(app)
        db.flush()
        db.commit()
        db.refresh(app)
        logger.info(f"[APPLICATION] Created application with ID: {app.id}")
        return app
    except Exception as err:
        db.rollback()
        logger.error(f"[APPLICATION] Failed to create application: {err}")
        return None


def get_application_by_id(
    db: Session,
    app_id: str
) -> Optional[Application]:
    """
    Retrieve a single application by its UUID.

    Args:
        db (Session): SQLAlchemy database session
        app_id (str): The UUID of the application to retrieve

    Returns:
        Optional[Appliation]: The Application object or None if not found
    """

    try:
        return db.query(Application).filter_by(id=app_id).one()
    except NoResultFound:
        logger.warning(f"[APPLICATION] Application '{app_id}' not found")
        return None
    except Exception as err:
        logger.error(
            f"[APPLICATION] Failed to retrieve application '{app_id}': {err}"
        )
        return None


def list_applications(
    db: Session,
    sort_fn: Optional[QueryMethod] = None,
    filter_fn: Optional[QueryMethod] = None,
    active_only: bool = False
) -> List[Application]:
    """
    Return all applications in the system with optional filtering and sorting.

    Args:
        db (Session): SQLAlchemy database session
        sort_fn (Optional[QueryMethod]): function to sort the query
        filter_fn (Optional[QueryMethod]): function to filter the query
        active_only (bool): If True, only return active applications

    Returns:
        List[Application]: List of Application objects
    """

    try:
        query: Query[Application] = db.query(Application)

        if active_only:
            query = query.filter(Application.is_active == True)

        if filter_fn is not None:
            query = filter_fn(query)

        if sort_fn is not None:
            query = sort_fn(query)

        return query.all()
    except Exception as err:
        logger.error(f"[APPLICATION] Failed to retrieve applications: {err}")
        return []


def update_application(
    db: Session,
    app_id: str,
    updates: Dict[str, Any]
) -> Optional[Application]:
    """
    Update application fields (URL, description, is_active, etc.).

    Args:
        db (Session): SQLAlchemy database session
        app_id (str): The UUID of the application to update
        updates: (dict): Dictionary of fields to update

    Returns:
        Optional[Application]: The updated Application object or
            None if update failed
    """

    valid_fields = {
        "url",
        "is_active",
        "description",
        "authentication_token"
    }
    updates = {
        k: v for k, v in updates.items()
        if k in valid_fields and v is not None
    }

    if not updates:
        logger.warning(f"[APPLICATION] No valid updates for '{app_id}'")
        return get_application_by_id(db, app_id)

    try:
        rows_updated = db.query(Application).filter_by(
            id=app_id
        ).update({
            getattr(Application, k): v for k, v in updates.items()
        })

        if rows_updated == 0:
            logger.warning(
                f"[APPLICATION] No application found with ID '{app_id}'"
            )
            return None

        db.commit()
        return get_application_by_id(db, app_id)

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
        app_id (str): The UUID of the application to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """

    try:
        app = db.query(Application).filter_by(id=app_id).one()
        db.delete(app)
        db.commit()
        logger.info(f"[APPLICATION] Deleted application '{app_id}'")
        return True
    except NoResultFound:
        logger.warning(
            f"[APPLICATION] Application '{app_id}' not found for deletion"
        )
        return False
    except Exception as err:
        db.rollback()
        logger.error(
            f"[APPLICATION] Failed to delete application '{app_id}': {err}"
        )
        return False
