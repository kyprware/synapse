"""
Static types for RPC payload base + batch data
"""

from typing import Union, List
from ..schemas.rpc_schema import RPCNotification, RPCRequest, RPCResponse


RPCData = Union[RPCRequest, RPCResponse, RPCNotification]
RPCBatchData = List[Union[RPCRequest, RPCResponse]]
RPCPayload = Union[RPCData, RPCBatchData]
