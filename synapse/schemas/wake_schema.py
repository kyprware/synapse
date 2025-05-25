from typing import List, Optional
from urllib.parse import urlparse
from pydantic import BaseModel, field_validator


class WakeResponseSchema(BaseModel):
    agent_id: str
    url: Optional[str] = None
    status_code: Optional[int] = None
    success: bool
    error: Optional[str] = None
    message: Optional[str] = None


class WakeRequestSchema(BaseModel):
    agent_ids: List[str]
