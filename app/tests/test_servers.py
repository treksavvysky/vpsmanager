import os
import json
import pytest
import pytest_asyncio
from httpx import AsyncClient
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["API_KEY"] = "testkey"

from app.database import Base, get_db
from app.models.server import Server
from main import app

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    with open("servers.json") as f:
        data = json.load(f)
    db = TestingSessionLocal()
    for idx, (name, cfg) in enumerate(data.items(), start=1):
        if name == "server1":
            continue
        ip = f"10.0.0.{idx}"
        db.add(
            Server(
                hostname=name,
                provider="LOCAL",
                public_ip=ip,
                role="dev",
                status="online",
                tags={},
            )
        )
    db.commit()
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    import main; main.API_KEY = "testkey"
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides = {}


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def auth_header():
    return {"Authorization": "testkey"}


@pytest.mark.asyncio
async def test_list_servers(client):
    r = await client.get("/servers", headers=auth_header())
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_create_get_update_delete(client):
    new_server = {
        "hostname": "example",
        "provider": "LOCAL",
        "public_ip": "1.2.3.4",
        "role": "dev",
        "status": "online",
        "tags": {"region": "us"}
    }
    resp = await client.post("/servers", json=new_server, headers=auth_header())
    assert resp.status_code == 200
    created = resp.json()
    sid = created["id"]

    # get
    resp = await client.get(f"/servers/{sid}", headers=auth_header())
    assert resp.status_code == 200
    assert resp.json()["hostname"] == "example"

    # update
    resp = await client.patch(f"/servers/{sid}", json={"status": "maintenance"}, headers=auth_header())
    assert resp.status_code == 200
    assert resp.json()["status"] == "maintenance"

    # delete
    resp = await client.delete(f"/servers/{sid}", headers=auth_header())
    assert resp.status_code == 204

    resp = await client.get(f"/servers/{sid}", headers=auth_header())
    assert resp.status_code == 404
