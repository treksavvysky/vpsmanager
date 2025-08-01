from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.credential import CredentialCreate, CredentialRead
from ..repositories.credential import CredentialRepository

router = APIRouter(prefix="/vault", tags=["vault"])

@router.post("/credentials", response_model=CredentialRead)
def create_credential(cred: CredentialCreate, db: Session = Depends(get_db)):
    """Store a new credential in the vault."""
    repo = CredentialRepository(db)
    return repo.create(cred)

@router.get("/credentials", response_model=List[CredentialRead])
def list_credentials(db: Session = Depends(get_db)):
    """List all credential names without revealing secrets."""
    repo = CredentialRepository(db)
    return repo.list()
