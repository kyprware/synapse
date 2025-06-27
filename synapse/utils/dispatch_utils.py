"""
JSON-RPC dispatch registry and execution logic.
"""

import logging
import importlib

from typing import (
    List,
    TypeVar,
    Optional,
    Callable,
    ParamSpec,
    Awaitable
)

from ..schemas.rpc_schema import (
    RPCRequest,
    RPCResponse,
    RPCResponseData,
    RPCError
)


P = ParamSpec("P")
R = TypeVar("R", bound=RPCResponse)

RPCHandler = Callable[P, Awaitable[R]]
RPCDispatchMethod = Callable[..., Awaitable[RPCResponseData]]

logger: logging.Logger = logging.getLogger(__name__)


class DispatchManager:
    """
    Manages the registration and retrieval of RPC handler functions.
    """

    def __init__(self, handler_modules: Optional[List[str]] = None):
        """
        Initialize the DispatchManager with an empty registry.

        Args:
            handler_modules: List of module paths to load handlers from
        """

        self._registry: dict[str, RPCDispatchMethod] = {}
        self._handler_modules = handler_modules or []
        self._loaded = False


    def register(
        self,
        name: str
    ) -> Callable[[RPCHandler], RPCHandler]:
        """
        Decorator to register an RPC handler function by name.

        Args:
            name (str): The method name to register.

        Returns:
            Callable: A decorator that registers the function.
        """

        def wrapper(func: RPCHandler) -> RPCHandler:
            self._registry[name] = func
            logger.debug(f"[DISPATCH] Registered RPC method: {name}")
            return func

        return wrapper


    def get_handler(self, name: str) -> Optional[RPCDispatchMethod]:
        """
        Retrieve a registered handler function by method name.

        Args:
            name (str): The name of the RPC method.

        Returns: Optional[Callable]: The handler function or None if not found.
        """

        if not self._loaded:
            self._load_handlers()

        return self._registry.get(name)


    def _load_handlers(self):
        """Load all configured handler modules."""

        if self._loaded:
            return

        for module_path in self._handler_modules:
            try:
                importlib.import_module(module_path)
                logger.debug(f"[DISPATCH] Loaded handler: {module_path}")
            except ImportError as e:
                logger.error(
                    f"[DISPATCH] Failed to load handler {module_path}: {e}"
                )

        self._loaded = True
        logger.info(f"[DISPATCH] Loaded {len(self._registry)} RPC handlers")


async def dispatch_rpc(
    dispatcher: DispatchManager,
    request: RPCRequest
) -> RPCResponse:
    """
    Dispatch an RPC request to a corresponding handler functions.

    Args:
        dispatcher (DispatchManager): The registered dispatcher instance.
        request (RPCRequest): an RPC request objects.

    Returns:
        RPCResponse: An RPC response objects.
    """

    handler = dispatcher.get_handler(request.method)

    if not handler:
        logger.warning(f"[DISPATCH] Unknown method: {request.method}")
        return RPCResponse(
            jsonrpc=request.jsonrpc,
            id=request.id,
            error=RPCError(
                code=-32601,
                message=f"Method '{request.method}' not found"
            )
        )


    try:
        response = await handler(**request.params or {})

        return RPCResponse(
            id=request.id,
            error=response.error,
            result=response.result,
        )
    except TypeError as err:
        logger.error(f"[DISPATCH] Param error in '{request.method}': {err}")
        return RPCResponse(
            jsonrpc=request.jsonrpc,
            id=request.id,
            error=RPCError(
                code=-32602,
                message=f"Invalid params: {err}"
            )
        )
    except Exception as err:
        logger.exception(f"[DISPATCH] Exception in '{request.method}'")
        return RPCResponse(
            jsonrpc=request.jsonrpc,
            id=request.id,
            error=RPCError(
                code=-32603,
                message=f"Internal error: {err}"
            )
        )
