from ..types.rpc_types import RPCAction
from ..config.db_config import SessionLocal
from ..config.dispatch_config import dispatcher
from ..schemas.rpc_schema import RPCResponseData, RPCError
from ..services.permission_services import (
    get_permissions_for_owner,
    get_permissions_for_target,
    grant_permission,
    revoke_permission,
    check_has_permission,
)


@dispatcher.register("get_permissions_for_owner")
async def rpc_get_permissions_for_owner(
    owner_id: str,
    active_only: bool = True
) -> RPCResponseData:
    """
    RPC handler to get all permissions owned by an application.

    Args:
        owner_id (str): The UUID of the application that owns the permissions.
        active_only (bool): If True, only return active permissions.

    Returns:
        RPCResponseData: The response with a list of permissions or an error.
    """

    with SessionLocal() as db:
        permissions = get_permissions_for_owner(db, owner_id, active_only)
        return RPCResponseData(
            result=[perm.to_dict() for perm in permissions]
        )


@dispatcher.register("get_permissions_for_target")
async def rpc_get_permissions_for_target(
    target_id: str,
    active_only: bool = True
) -> RPCResponseData:
    """
    RPC handler to get all permissions that affect an application.

    Args:
        target_id (str): The UUID of the application that is the target.
        active_only (bool): If True, only return active permissions.

    Returns:
        RPCResponseData: The response with a list of permissions or an error.
    """

    with SessionLocal() as db:
        permissions = get_permissions_for_target(db, target_id, active_only)
        return RPCResponseData(
            result=[perm.to_dict() for perm in permissions]
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


@dispatcher.register("check_has_permission")
async def rpc_check_has_permission(
    owner_id: str,
    target_id: str,
    action: str,
    active_only: bool = True
) -> RPCResponseData:
    """
    RPC handler to check if a permission exists between applications.

    Args:
        owner_id (str): The UUID of the application that should own the
            permission.
        target_id (str): The UUID of the application that should be the target.
        action (str): The action to check for.
        active_only (bool): If True, only check active permissions.

    Returns:
        RPCResponseData: The response with the permission check result.
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
        has_permission = check_has_permission(
            db, owner_id, target_id, rpc_action, active_only
        )
        return RPCResponseData(
            result={"has_permission": has_permission}
        )
