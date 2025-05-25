from uuid import UUID
from typing import  Optional, Any
from urllib.parse import urlparse
from pydantic import BaseModel, field_validator


class AgentSchema(BaseModel):
    uuid: str
    api_key: str
    ping_url: str

    @field_validator("uuid")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        try:
            UUID(v)
        except (ValueError, TypeError):
            raise ValueError("Invalid UUID string")
        return v

    @field_validator("ping_url")
    @classmethod
    def validate_ping_url(cls, v: str) -> str:
        parsed = urlparse(v)

        if not (parsed.scheme and parsed.netloc):
            raise ValueError("Invalid URL format")
        return v


class AgentUpdateSchema(AgentSchema):
    uuid: Optional[str] = None
    api_key: Optional[str] = None
    ping_url: Optional[str] = None


class AgentResponseSchema(BaseModel):
    data: Any
    detail: str
