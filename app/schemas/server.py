from uuid import UUID
from typing import Dict, Optional
from pydantic import BaseModel, constr

# Allow more flexible hostname patterns for IPs and domains
HostnamePattern = constr(pattern=r"^[a-zA-Z0-9.-]{1,255}$")


class ServerBase(BaseModel):
    hostname: HostnamePattern
    provider: str
    public_ip: str  # Changed from IPvAnyAddress to str to allow domains
    role: str
    status: str = "online"
    tags: Dict[str, str] = {}


class ServerCreate(ServerBase):
    pass


class ServerUpdate(BaseModel):
    role: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class ServerRead(ServerBase):
    id: UUID

    class Config:
        from_attributes = True  # Updated for Pydantic v2
