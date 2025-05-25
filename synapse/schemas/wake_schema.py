from pydantic import BaseModel
from typing import List, Optional


class WakeResponseSchema(BaseModel):
    agent_id: str
    url: Optional[str] = None
    status_code: Optional[int] = None
    success: bool
    error: Optional[str] = None
    message: Optional[str] = None


class WakeRequestSchema(BaseModel):
    agent_ids: List[str]
