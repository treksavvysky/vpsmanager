from uuid import uuid4
from enum import Enum
from sqlalchemy import Column, String, Enum as SqlEnum, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base


class Provider(str, Enum):
    IONOS = "IONOS"
    AWS = "AWS"
    LOCAL = "LOCAL"


class Role(str, Enum):
    prod = "prod"
    dev = "dev"
    exp = "exp"


class Status(str, Enum):
    online = "online"
    maintenance = "maintenance"
    retired = "retired"


class Server(Base):
    __tablename__ = "servers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    hostname = Column(String(255), nullable=False)
    provider = Column(SqlEnum(Provider), nullable=False)
    public_ip = Column(String, unique=True, nullable=False)
    role = Column(SqlEnum(Role), nullable=False)
    status = Column(SqlEnum(Status), nullable=False, default=Status.online)
    tags = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
