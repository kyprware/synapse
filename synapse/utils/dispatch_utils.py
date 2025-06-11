"""
JSON-RPC dispatch registry and execution logic.
"""

import logging
import inspect
from typing import (
    List,
    Union,
    TypeVar,
    Optional,
    Callable,
    ParamSpec,
    Awaitable
)

from ..schemas.rpc_schema import RPCRequest, RPCResponse, RPCError


R = TypeVar("R")
P = ParamSpec("P")

RPCDispatchMethod = Callable[..., Union[R, Awaitable[R]]]

logger: logging.Logger = logging.getLogger(__name__)


class DispatchManager:
    """
    Manages the registration and retrieval of RPC handler functions.
    """

    def __init__(self):
        """
        Initialize the DispatchManager with an empty registry.
        """

        self._registry: dict[str, RPCDispatchMethod] = {}


    def register(
        self,
        name: str
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """
        Decorator to register an RPC handler function by name.

        Args:
            name (str): The method name to register.

        Returns:
            Callable: A decorator that registers the function.
        """

        def wrapper(func: Callable[P, R]) -> Callable[P, R]:
            self._registry[name] = func
            logger.debug(f"[DISPATCH] Registered RPC method: {name}")
            return func

        return wrapper


    def get_handler(self, name: str) -> Optional[RPCDispatchMethod]:
        """
        Retrieve a registered handler function by method name.

        Args:
            name (str): The name of the RPC method.

        Returns:
            Optional[Callable]: The handler function or None if not found.
        """

        return self._registry.get(name)


async def dispatch_rpcs(
    dispatcher: DispatchManager,
    *requests: RPCRequest
) -> List[RPCResponse]:
    """
    Dispatch multiple RPC requests to their corresponding handler functions.

    Args:
        dispatcher (DispatchManager): The registered dispatcher instance.
        *requests (RPCRequest): One or more parsed RPC request objects.

    Returns:
        List[RPCResponse]: A list of RPC response objects.
    """

    responses: List[RPCResponse] = []

    for request in requests:
        handler = dispatcher.get_handler(request.method)

        if not handler:
            responses.append(RPCResponse(
                jsonrpc=request.jsonrpc,
                id=request.id,
                error=RPCError(
                    code=-32601,
                    message=f"Method '{request.method}' not found"
                )
            ))

            logger.warning(f"[DISPATCH] Unknown method: {request.method}")

            continue

        try:
            params: dict = request.params or {}

            if inspect.iscoroutinefunction(handler):
                result = await handler(**params)
            else:
                result = handler(**params)

            responses.append(RPCResponse(
                jsonrpc=request.jsonrpc,
                id=request.id,
                result=result
            ))

        except TypeError as err:
            responses.append(RPCResponse(
                jsonrpc=request.jsonrpc,
                id=request.id,
                error=RPCError(
                    code=-32602,
                    message=f"Invalid params: {err}"
                )
            ))

            logger.error(
                f"[DISPATCH] Param error in '{request.method}': {err}"
            )

        except Exception as err:
            responses.append(RPCResponse(
                jsonrpc=request.jsonrpc,
                id=request.id,
                error=RPCError(
                    code=-32603,
                    message=f"Internal error: {err}"
                )
            ))

            logger.exception(f"[DISPATCH] Exception in '{request.method}'")

    return responses
