from uuid import UUID
from pydantic import BaseModel
from ..models.credential import CredentialType

class CredentialBase(BaseModel):
    name: str
    type: CredentialType

class CredentialCreate(CredentialBase):
    secret: str

class CredentialRead(CredentialBase):
    id: UUID

    class Config:
        from_attributes = True
