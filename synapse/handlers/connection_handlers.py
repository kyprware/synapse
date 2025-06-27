import logging
from asyncio import StreamWriter

from ..utils.jwt_utils import verify_token
from ..config.dispatch_config import dispatcher
from ..services.connection_services import add_connection
from ..schemas.rpc_schema import RPCResponseData, RPCError


logger = logging.getLogger(__name__)


@dispatcher.register("connect")
async def connect_application(
    id: str,
    writer: StreamWriter,
    authentication_token: str
) -> RPCResponseData:
    """
    Handle application connection requests.

    Args:
        id (str): Application identifier
        writer (StreamWriter): Stream writer for the connection
        authentication_token (str): JWT authentication token

    Returns:
        RPCResponseData: Response data containing connection status
    """

    try:
        payload = verify_token(authentication_token)

        if not payload:
            return RPCResponseData(
                error=RPCError(
                    code=-32603,
                    message="Authentication token is invalid or expired"
                )
            )

        connection = add_connection(id, writer)
        logger.info(f"[CONNECT] Application {id} connected successfully")
        return RPCResponseData(
            data={
                "connection_id": connection.id,
                "message": "Application connected successfully"
            }
        )

    except Exception as e:
        logger.error(f"[CONNECT] Error connecting application {id}: {str(e)}")
        return RPCResponseData(
            error=RPCError(
                code="CONNECTION_ERROR",
                message=f"Failed to connect application: {str(e)}"
            )
        )
