from ..config.db_config import SessionLocal
from ..config.dispatch_config import dispatcher
from ..schemas.rpc_schema import RPCResponseData, RPCError
from ..services.application_services import (
    create_application,
    get_application_by_id,
    list_applications,
    update_application,
    delete_application,
)


@dispatcher.register("create_application")
async def rpc_create_application(
    url: str,
    description: str,
    authentication_token: str | None = None
) -> RPCResponseData:
    """
    RPC handler to create a new application.

    Args:
        url (str): The URL of the application to create.
        description (str): Optional description of the application.
        authentication_token (str | None): Optional authentication token.

    Returns:
        RPCResponseData: RPC response with the created application or an error.
    """

    with SessionLocal() as db:
        app = create_application(
            db,
            url=url,
            description=description,
            authentication_token=authentication_token
        )

        if app:
            return RPCResponseData(
                result=app.to_dict()
            )
        return RPCResponseData(
            error=RPCError(
                code=-32000,
                message="Failed to create application"
            )
        )


@dispatcher.register("read_application")
async def rpc_read_application(id: str) -> RPCResponseData:
    """
    RPC handler to retrieve an application by ID.

    Args:
        id (str): The unique ID of the application.

    Returns:
        RPCResponseData: RPC response with the application or an error.
    """

    with SessionLocal() as db:
        app = get_application_by_id(db, id)

        if app:
            return RPCResponseData(
                result=app.to_dict()
            )

        return RPCResponseData(
            error=RPCError(
                code=-32001,
                message="Application not found"
            )
        )


@dispatcher.register("list_applications")
async def rpc_list_applications(active_only: bool = False) -> RPCResponseData:
    """
    RPC handler to fetch applications with optional filtering and sorting.

    Args:
        active_only (bool): If True, only return active applications.

    Returns:
        RPCResponseData: RPC response with a list of applications or an error.
    """

    with SessionLocal() as db:
        apps = list_applications(
            db,
            active_only=active_only
        )

        return RPCResponseData(
            result=[app.to_dict() for app in apps]
        )


@dispatcher.register("update_application")
async def rpc_update_application(
    id: str,
    updates: dict
) -> RPCResponseData:
    """
    RPC handler to update an application.

    Args:
        id (str): The ID of the application to update.
        updates (dict): A dictionary of fields to update.

    Returns:
        RPCResponseData: RPC response with the updated application or an error.
    """

    with SessionLocal() as db:
        app = update_application(db, id, updates)

        if app:
            return RPCResponseData(
                result=app.to_dict()
            )

        return RPCResponseData(
            error=RPCError(
                code=-32002,
                message="Failed to update application"
            )
        )


@dispatcher.register("delete_application")
async def rpc_delete_application(id: str) -> RPCResponseData:
    """
    RPC handler to delete an application.

    Args:
        id (str): The ID of the application to delete.

    Returns:
        RPCResponseData: RPC response indicating success/failure or an error.
    """

    with SessionLocal() as db:
        success = delete_application(db, id)

        if success:
            return RPCResponseData(
                result={ "success": True }
            )

        return RPCResponseData(
            error=RPCError(
                code=-32003,
                message="Failed to delete application"
            )
        )
