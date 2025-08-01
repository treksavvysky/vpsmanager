from uuid import uuid4
from enum import Enum
from sqlalchemy import Column, String, Enum as SqlEnum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base

class CredentialType(str, Enum):
    ssh_key = "ssh_key"
    password = "password"

class Credential(Base):
    """Model representing an encrypted credential."""

    __tablename__ = "credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), unique=True, nullable=False)
    type = Column(SqlEnum(CredentialType), nullable=False)
    secret = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
