from uuid import UUID
from typing import Dict, Optional
from pydantic import BaseModel, IPvAnyAddress, constr

DnsLabel = constr(pattern=r"^[a-z0-9-]{1,63}$")


class ServerBase(BaseModel):
    hostname: DnsLabel
    provider: str
    public_ip: IPvAnyAddress
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
        orm_mode = True
