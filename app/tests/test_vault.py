import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet

os.environ["API_KEY"] = "testkey"
os.environ.setdefault("VAULT_KEY", Fernet.generate_key().decode())

from app.database import Base, get_db
from main import app

DATABASE_URL = "sqlite:///./vault_test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    import main
    main.API_KEY = "testkey"
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides = {}


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_create_and_list_credentials(client):
    cred = {"name": "test-key", "type": "ssh_key", "secret": "dummy"}
    resp = await client.post("/vault/credentials", json=cred, headers={"Authorization": "testkey"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "test-key"
    assert data["type"] == "ssh_key"
    assert "secret" not in data

    resp = await client.get("/vault/credentials", headers={"Authorization": "testkey"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "test-key"

