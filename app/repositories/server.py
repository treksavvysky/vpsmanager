from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..models.server import Server
from ..schemas.server import ServerCreate, ServerUpdate


class ServerRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        provider: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Server]:
        query = self.db.query(Server)
        if provider:
            query = query.filter(Server.provider == provider)
        if role:
            query = query.filter(Server.role == role)
        if status:
            query = query.filter(Server.status == status)
        return query.offset(skip).limit(limit).all()

    def get(self, server_id: UUID) -> Optional[Server]:
        return self.db.query(Server).filter(Server.id == server_id).first()

    def create(self, obj: ServerCreate) -> Server:
        db_obj = Server(
            hostname=obj.hostname,
            provider=obj.provider,
            public_ip=str(obj.public_ip),
            role=obj.role,
            status=obj.status,
            tags=obj.tags,
        )
        self.db.add(db_obj)
        try:
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            self.db.rollback()
            if "UNIQUE constraint failed: servers.public_ip" in str(e):
                raise HTTPException(status_code=400, detail="Server with this IP address already exists")
            else:
                raise HTTPException(status_code=400, detail="Database constraint violation")

    def update(self, db_obj: Server, obj_in: ServerUpdate) -> Server:
        if obj_in.role is not None:
            db_obj.role = obj_in.role
        if obj_in.status is not None:
            db_obj.status = obj_in.status
        if obj_in.tags is not None:
            db_obj.tags = obj_in.tags
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: Server) -> None:
        self.db.delete(db_obj)
        self.db.commit()
