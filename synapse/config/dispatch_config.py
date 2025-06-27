"""
JSON-RPC dispatch manager configuration
"""

from ..utils.dispatch_utils import DispatchManager


dispatcher = DispatchManager(handler_modules=[
    "synapse.handlers.connection_handlers",
    "synapse.handlers.application_handlers",
    "synapse.handlers.application_permission_handlers"
])
