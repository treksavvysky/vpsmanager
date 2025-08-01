from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..models.credential import Credential, CredentialType
from ..schemas.credential import CredentialCreate
from ..utils.vault import encrypt_secret, decrypt_secret

class CredentialRepository:
    """Repository for managing Credential objects."""

    def __init__(self, db: Session):
        self.db = db

    def list(self) -> List[Credential]:
        return self.db.query(Credential).all()

    def get_by_name(self, name: str) -> Optional[Credential]:
        return self.db.query(Credential).filter(Credential.name == name).first()

    def create(self, obj: CredentialCreate) -> Credential:
        encrypted = encrypt_secret(obj.secret)
        db_obj = Credential(name=obj.name, type=obj.type, secret=encrypted)
        self.db.add(db_obj)
        try:
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Credential with this name already exists")

    def delete(self, db_obj: Credential) -> None:
        self.db.delete(db_obj)
        self.db.commit()
