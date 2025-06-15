"""
Static types for RPC payload base + batch data
"""

from enum import Enum
from typing import Union, List
from ..schemas.rpc_schema import RPCNotification, RPCRequest, RPCResponse


class RPCAction(str, Enum):
    """
    Class enum for rpc actions
    """

    INBOUND_REQUEST = "inbound_request"
    INBOUND_RESPONSE = "inbound_response"
    INBOUND_NOTIFICATION = "inbound_notification"

    OUTBOUND_REQUEST = "outbound_request"
    OUTBOUND_RESPONSE = "outbound_response"
    OUTBOUND_NOTIFICATION = "outbound_notification"


RPCData = Union[RPCRequest, RPCResponse, RPCNotification]
RPCBatchData = List[Union[RPCRequest, RPCResponse]]
RPCPayload = Union[RPCData, RPCBatchData]
