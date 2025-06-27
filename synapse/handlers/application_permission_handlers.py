from ..types.rpc_types import RPCAction
from ..config.db_config import SessionLocal
from ..config.dispatch_config import dispatcher
from ..schemas.rpc_schema import RPCResponseData, RPCError
from ..services.permission_services import (
    grant_permission,
    revoke_permission,
)


@dispatcher.register("grant_permission")
async def rpc_grant_permission(
    owner_id: str,
    target_id: str,
    action: str
) -> RPCResponseData:
    """
    RPC handler to grant a permission between applications.

    Args:
        owner_id (str): The UUID of the application granting the permission.
        target_id (str): The UUID of the application receiving the permission.
        action (str): The action being permitted.

    Returns:
        RPCResponseData: The response with the created permission or an error.
    """

    try:
        rpc_action = RPCAction(action)
    except ValueError:
        return RPCResponseData(
            error=RPCError(
                code=-32004,
                message=f"Invalid action: {action}"
            )
        )

    with SessionLocal() as db:
        permission = grant_permission(db, owner_id, target_id, rpc_action)

        if permission:
            return RPCResponseData(
                result=permission.to_dict()
            )

        return RPCResponseData(
            error=RPCError(
                code=-32005,
                message="Failed to grant permission"
            )
        )


@dispatcher.register("revoke_permission")
async def rpc_revoke_permission(
    owner_id: str,
    target_id: str,
    action: str
) -> RPCResponseData:
    """
    RPC handler to revoke a permission between applications.

    Args:
        owner_id (str): The UUID of the application that owns the permission.
        target_id (str): The UUID of the application that is the target.
        action (str): The action to revoke.

    Returns:
        RPCResponseData: The response indicating success or failure.
    """

    try:
        rpc_action = RPCAction(action)
    except ValueError:
        return RPCResponseData(
            error=RPCError(
                code=-32004,
                message=f"Invalid action: {action}"
            )
        )

    with SessionLocal() as db:
        success = revoke_permission(db, owner_id, target_id, rpc_action)

        if success:
            return RPCResponseData(
                result={"success": True}
            )

        return RPCResponseData(
            error=RPCError(
                code=-32006,
                message="Failed to revoke permission"
            )
        )
