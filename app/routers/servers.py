from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..repositories.server import ServerRepository
from ..schemas.server import ServerCreate, ServerRead, ServerUpdate

router = APIRouter(prefix="/servers", tags=["servers"])


@router.get("", response_model=List[ServerRead])
def list_servers(
    provider: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    repo = ServerRepository(db)
    return repo.list(skip=offset, limit=limit, provider=provider, role=role, status=status)


@router.post("", response_model=ServerRead)
def create_server(server: ServerCreate, db: Session = Depends(get_db)):
    repo = ServerRepository(db)
    return repo.create(server)


@router.get("/{server_id}", response_model=ServerRead)
def get_server(server_id: UUID, db: Session = Depends(get_db)):
    repo = ServerRepository(db)
    db_obj = repo.get(server_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_obj


@router.patch("/{server_id}", response_model=ServerRead)
def update_server(server_id: UUID, update: ServerUpdate, db: Session = Depends(get_db)):
    repo = ServerRepository(db)
    db_obj = repo.get(server_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Server not found")
    return repo.update(db_obj, update)


@router.delete("/{server_id}", status_code=204)
def delete_server(server_id: UUID, db: Session = Depends(get_db)):
    repo = ServerRepository(db)
    db_obj = repo.get(server_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Server not found")
    repo.delete(db_obj)
