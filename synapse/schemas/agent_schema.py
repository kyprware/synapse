from uuid import UUID
from urllib.parse import urlparse
from typing import  Optional, Any
from pydantic import BaseModel, field_validator


def validate_url(_, v: str) -> str:
    parsed = urlparse(v)

    if not (parsed.scheme and parsed.netloc):
        raise ValueError("Invalid URL format")
    return v


def validate_uuid(_, v: str) -> str:
    try:
        UUID(v)
    except (ValueError, TypeError):
        raise ValueError("Invalid UUID string")
    return v


class AgentCreateSchema(BaseModel):
    uuid: str
    api_key: str
    ping_url: str

    @field_validator("uuid")
    @classmethod
    def uuid_validator(cls, v: str) -> str:
        return validate_url(cls, v)

    @field_validator("ping_url")
    @classmethod
    def ping_url_validator(cls, v: str) -> str:
        return validate_uuid(cls, v)


class AgentUpdateSchema(BaseModel):
    uuid: Optional[str] = None
    api_key: Optional[str] = None
    ping_url: Optional[str] = None

    @field_validator("uuid")
    @classmethod
    def uuid_validator(cls, v: str) -> str:
        return validate_url(cls, v)

    @field_validator("ping_url")
    @classmethod
    def ping_url_validator(cls, v: str) -> str:
        return validate_uuid(cls, v)


class AgentResponseSchema(BaseModel):
    data: Any
    detail: str
