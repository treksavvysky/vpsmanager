import os
import json
import pytest
import pytest_asyncio
from httpx import AsyncClient
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

os.environ["API_KEY"] = "testkey"

from app.database import Base, get_db
from app.models.server import Server, Provider, Role, Status
from main import app

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def setup_db():
    """Set up test database with fresh data for each test."""
    Base.metadata.create_all(bind=engine)
    
    # Create test data
    db = TestingSessionLocal()
    test_servers = [
        Server(
            hostname="test-server-1",
            provider=Provider.LOCAL,
            public_ip="10.0.0.1",
            role=Role.dev,
            status=Status.online,
            tags={"environment": "test", "team": "backend"},
        ),
        Server(
            hostname="test-server-2", 
            provider=Provider.AWS,
            public_ip="10.0.0.2",
            role=Role.prod,
            status=Status.online,
            tags={"environment": "production", "team": "frontend"},
        ),
        Server(
            hostname="maintenance-server",
            provider=Provider.IONOS,
            public_ip="10.0.0.3",
            role=Role.exp,
            status=Status.maintenance,
            tags={"environment": "experimental"},
        )
    ]
    
    for server in test_servers:
        db.add(server)
    db.commit()
    db.close()

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
    """HTTP client for testing API endpoints."""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def auth_header():
    """Helper function to get authentication headers."""
    return {"Authorization": "testkey"}


# Test authentication and authorization
@pytest.mark.asyncio
async def test_authentication_required(client):
    """Test that API endpoints require authentication."""
    # No auth header
    resp = await client.get("/servers")
    assert resp.status_code == 403  # FastAPI returns 403 for missing API key
    
    # Invalid auth
    resp = await client.get("/servers", headers={"Authorization": "invalid"})
    assert resp.status_code == 401  # Invalid key returns 401
    
    # Valid auth should work
    resp = await client.get("/servers", headers=auth_header())
    assert resp.status_code == 200


# Test server listing and filtering
@pytest.mark.asyncio
async def test_list_servers_basic(client):
    """Test basic server listing functionality."""
    resp = await client.get("/servers", headers=auth_header())
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    
    # Verify response structure
    server = data[0]
    required_fields = ["id", "hostname", "provider", "public_ip", "role", "status", "tags"]
    for field in required_fields:
        assert field in server


@pytest.mark.asyncio
async def test_list_servers_filter_by_provider(client):
    """Test filtering servers by provider."""
    # Filter by AWS
    resp = await client.get("/servers?provider=AWS", headers=auth_header())
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["provider"] == "AWS"
    
    # Filter by LOCAL
    resp = await client.get("/servers?provider=LOCAL", headers=auth_header())
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["provider"] == "LOCAL"
    
    # Filter by non-existent provider
    resp = await client.get("/servers?provider=NONEXISTENT", headers=auth_header())
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_list_servers_filter_by_role(client):
    """Test filtering servers by role."""
    resp = await client.get("/servers?role=prod", headers=auth_header())
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["role"] == "prod"


@pytest.mark.asyncio
async def test_list_servers_filter_by_status(client):
    """Test filtering servers by status."""
    resp = await client.get("/servers?status=maintenance", headers=auth_header())
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["status"] == "maintenance"


@pytest.mark.asyncio
async def test_list_servers_multiple_filters(client):
    """Test filtering servers with multiple parameters."""
    resp = await client.get("/servers?provider=AWS&role=prod&status=online", headers=auth_header())
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["provider"] == "AWS"
    assert data[0]["role"] == "prod"
    assert data[0]["status"] == "online"


@pytest.mark.asyncio
async def test_list_servers_pagination(client):
    """Test server listing with pagination."""
    # Test limit
    resp = await client.get("/servers?limit=2", headers=auth_header())
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    
    # Test offset
    resp = await client.get("/servers?offset=1&limit=2", headers=auth_header())
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


# Test server creation
@pytest.mark.asyncio
async def test_create_server_valid(client):
    """Test creating a server with valid data."""
    new_server = {
        "hostname": "new-test-server",
        "provider": "AWS",
        "public_ip": "192.168.1.1",
        "role": "dev",
        "status": "online",
        "tags": {"team": "devops", "project": "alpha"}
    }
    
    resp = await client.post("/servers", json=new_server, headers=auth_header())
    assert resp.status_code == 200
    
    created = resp.json()
    assert created["hostname"] == new_server["hostname"]
    assert created["provider"] == new_server["provider"]
    assert created["public_ip"] == new_server["public_ip"]
    assert created["role"] == new_server["role"]
    assert created["status"] == new_server["status"]
    assert created["tags"] == new_server["tags"]
    assert "id" in created


@pytest.mark.asyncio
async def test_create_server_minimal_data(client):
    """Test creating a server with minimal required data."""
    new_server = {
        "hostname": "minimal-server",
        "provider": "LOCAL",
        "public_ip": "127.0.0.1", 
        "role": "dev"
    }
    
    resp = await client.post("/servers", json=new_server, headers=auth_header())
    assert resp.status_code == 200
    
    created = resp.json()
    assert created["hostname"] == new_server["hostname"]
    assert created["status"] == "online"  # default value
    assert created["tags"] == {}  # default value


@pytest.mark.asyncio
async def test_create_server_duplicate_ip(client):
    """Test that creating a server with duplicate IP fails."""
    new_server = {
        "hostname": "duplicate-ip-server",
        "provider": "AWS",
        "public_ip": "10.0.0.1",  # This IP already exists
        "role": "dev"
    }
    
    resp = await client.post("/servers", json=new_server, headers=auth_header())
    assert resp.status_code == 400  # Should return 400 with proper error handling
    assert "already exists" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_create_server_invalid_data(client):
    """Test creating a server with invalid data."""
    # Missing required fields
    resp = await client.post("/servers", json={}, headers=auth_header())
    assert resp.status_code == 422
    
    # Invalid hostname pattern
    invalid_server = {
        "hostname": "invalid@hostname!",
        "provider": "AWS",
        "public_ip": "1.2.3.4",
        "role": "dev"
    }
    resp = await client.post("/servers", json=invalid_server, headers=auth_header())
    assert resp.status_code == 422


# Test server retrieval
@pytest.mark.asyncio
async def test_get_server_by_id(client):
    """Test retrieving a specific server by ID."""
    # First get list to find an ID
    resp = await client.get("/servers", headers=auth_header())
    servers = resp.json()
    server_id = servers[0]["id"]
    
    # Get specific server
    resp = await client.get(f"/servers/{server_id}", headers=auth_header())
    assert resp.status_code == 200
    
    server = resp.json()
    assert server["id"] == server_id
    assert "hostname" in server


@pytest.mark.asyncio
async def test_get_server_not_found(client):
    """Test retrieving a non-existent server."""
    fake_id = str(uuid4())
    resp = await client.get(f"/servers/{fake_id}", headers=auth_header())
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_server_invalid_uuid(client):
    """Test retrieving a server with invalid UUID format."""
    resp = await client.get("/servers/invalid-uuid", headers=auth_header())
    assert resp.status_code == 422


# Test server updates
@pytest.mark.asyncio
async def test_update_server_role(client):
    """Test updating a server's role."""
    # Get a server ID
    resp = await client.get("/servers", headers=auth_header())
    server_id = resp.json()[0]["id"]
    
    # Update role
    update_data = {"role": "prod"}
    resp = await client.patch(f"/servers/{server_id}", json=update_data, headers=auth_header())
    assert resp.status_code == 200
    
    updated = resp.json()
    assert updated["role"] == "prod"


@pytest.mark.asyncio
async def test_update_server_status(client):
    """Test updating a server's status."""
    # Get a server ID
    resp = await client.get("/servers", headers=auth_header())
    server_id = resp.json()[0]["id"]
    
    # Update status
    update_data = {"status": "maintenance"}
    resp = await client.patch(f"/servers/{server_id}", json=update_data, headers=auth_header())
    assert resp.status_code == 200
    
    updated = resp.json()
    assert updated["status"] == "maintenance"


@pytest.mark.asyncio
async def test_update_server_tags(client):
    """Test updating a server's tags."""
    # Get a server ID
    resp = await client.get("/servers", headers=auth_header())
    server_id = resp.json()[0]["id"]
    
    # Update tags
    new_tags = {"updated": "true", "version": "2.0"}
    update_data = {"tags": new_tags}
    resp = await client.patch(f"/servers/{server_id}", json=update_data, headers=auth_header())
    assert resp.status_code == 200
    
    updated = resp.json()
    assert updated["tags"] == new_tags


@pytest.mark.asyncio
async def test_update_server_multiple_fields(client):
    """Test updating multiple server fields at once."""
    # Get a server ID
    resp = await client.get("/servers", headers=auth_header())
    server_id = resp.json()[0]["id"]
    
    # Update multiple fields
    update_data = {
        "role": "exp",
        "status": "retired",
        "tags": {"retired": "true", "date": "2025-07-31"}
    }
    resp = await client.patch(f"/servers/{server_id}", json=update_data, headers=auth_header())
    assert resp.status_code == 200
    
    updated = resp.json()
    assert updated["role"] == "exp"
    assert updated["status"] == "retired"
    assert updated["tags"]["retired"] == "true"


@pytest.mark.asyncio
async def test_update_server_not_found(client):
    """Test updating a non-existent server."""
    fake_id = str(uuid4())
    update_data = {"status": "maintenance"}
    resp = await client.patch(f"/servers/{fake_id}", json=update_data, headers=auth_header())
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_server_empty_update(client):
    """Test updating a server with no changes."""
    # Get a server ID
    resp = await client.get("/servers", headers=auth_header())
    server_id = resp.json()[0]["id"]
    
    # Send empty update
    resp = await client.patch(f"/servers/{server_id}", json={}, headers=auth_header())
    assert resp.status_code == 200


# Test server deletion
@pytest.mark.asyncio
async def test_delete_server(client):
    """Test deleting a server."""
    # Get a server ID
    resp = await client.get("/servers", headers=auth_header())
    server_id = resp.json()[0]["id"]
    initial_count = len(resp.json())
    
    # Delete the server
    resp = await client.delete(f"/servers/{server_id}", headers=auth_header())
    assert resp.status_code == 204
    
    # Verify it's gone
    resp = await client.get(f"/servers/{server_id}", headers=auth_header())
    assert resp.status_code == 404
    
    # Verify list count decreased
    resp = await client.get("/servers", headers=auth_header())
    assert len(resp.json()) == initial_count - 1


@pytest.mark.asyncio
async def test_delete_server_not_found(client):
    """Test deleting a non-existent server."""
    fake_id = str(uuid4())
    resp = await client.delete(f"/servers/{fake_id}", headers=auth_header())
    assert resp.status_code == 404


# Test complete CRUD workflow
@pytest.mark.asyncio
async def test_complete_crud_workflow(client):
    """Test complete Create, Read, Update, Delete workflow."""
    # CREATE
    new_server = {
        "hostname": "crud-test-server",
        "provider": "AWS",
        "public_ip": "203.0.113.1",
        "role": "dev",
        "status": "online",
        "tags": {"test": "crud", "workflow": "complete"}
    }
    
    resp = await client.post("/servers", json=new_server, headers=auth_header())
    assert resp.status_code == 200
    created = resp.json()
    server_id = created["id"]
    
    # READ - Get specific server
    resp = await client.get(f"/servers/{server_id}", headers=auth_header())
    assert resp.status_code == 200
    retrieved = resp.json()
    assert retrieved["hostname"] == new_server["hostname"]
    assert retrieved["provider"] == new_server["provider"]
    
    # READ - Verify in list
    resp = await client.get("/servers", headers=auth_header())
    assert resp.status_code == 200
    servers = resp.json()
    server_ids = [s["id"] for s in servers]
    assert server_id in server_ids
    
    # UPDATE
    update_data = {
        "role": "prod",
        "status": "maintenance", 
        "tags": {"test": "crud", "workflow": "updated", "version": "2"}
    }
    resp = await client.patch(f"/servers/{server_id}", json=update_data, headers=auth_header())
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["role"] == "prod"
    assert updated["status"] == "maintenance"
    assert updated["tags"]["version"] == "2"
    
    # READ after update
    resp = await client.get(f"/servers/{server_id}", headers=auth_header())
    assert resp.status_code == 200
    retrieved_after_update = resp.json()
    assert retrieved_after_update["role"] == "prod"
    assert retrieved_after_update["status"] == "maintenance"
    
    # DELETE
    resp = await client.delete(f"/servers/{server_id}", headers=auth_header())
    assert resp.status_code == 204
    
    # READ after delete - should be 404
    resp = await client.get(f"/servers/{server_id}", headers=auth_header())
    assert resp.status_code == 404
    
    # Verify not in list
    resp = await client.get("/servers", headers=auth_header())
    assert resp.status_code == 200
    servers_after_delete = resp.json()
    server_ids_after_delete = [s["id"] for s in servers_after_delete]
    assert server_id not in server_ids_after_delete


# Test edge cases and error handling
@pytest.mark.asyncio
async def test_various_hostname_formats(client):
    """Test that various hostname formats are accepted."""
    valid_hostnames = [
        "simple-hostname",
        "example.com",
        "sub.domain.example.com",
        "192.168.1.1",
        "server-01.datacenter-us-east-1.company.com"
    ]
    
    created_servers = []
    for i, hostname in enumerate(valid_hostnames):
        server_data = {
            "hostname": hostname,
            "provider": "LOCAL",
            "public_ip": f"192.168.100.{i+1}",
            "role": "dev"
        }
        
        resp = await client.post("/servers", json=server_data, headers=auth_header())
        assert resp.status_code == 200, f"Failed to create server with hostname: {hostname}"
        created_servers.append(resp.json()["id"])
    
    # Cleanup
    for server_id in created_servers:
        await client.delete(f"/servers/{server_id}", headers=auth_header())


@pytest.mark.asyncio
async def test_enum_values_validation(client):
    """Test that enum values are properly validated."""
    # Valid enum values
    valid_server = {
        "hostname": "enum-test",
        "provider": "IONOS",  # Valid Provider enum
        "public_ip": "203.0.113.2",
        "role": "exp",  # Valid Role enum
        "status": "retired"  # Valid Status enum
    }
    
    resp = await client.post("/servers", json=valid_server, headers=auth_header())
    assert resp.status_code == 200
    
    server_id = resp.json()["id"]
    
    # Test valid enum values in updates
    valid_updates = [
        {"role": "prod"},
        {"status": "maintenance"},
    ]
    
    for valid_update in valid_updates:
        resp = await client.patch(f"/servers/{server_id}", json=valid_update, headers=auth_header())
        assert resp.status_code == 200
    
    # Cleanup
    await client.delete(f"/servers/{server_id}", headers=auth_header())


# Test concurrent operations (basic)
@pytest.mark.asyncio
async def test_concurrent_server_creation(client):
    """Test creating multiple servers concurrently."""
    import asyncio
    
    async def create_server(index):
        server_data = {
            "hostname": f"concurrent-server-{index}",
            "provider": "LOCAL",
            "public_ip": f"10.10.10.{index}",
            "role": "dev"
        }
        return await client.post("/servers", json=server_data, headers=auth_header())
    
    # Create 5 servers concurrently
    tasks = [create_server(i) for i in range(1, 6)]
    responses = await asyncio.gather(*tasks)
    
    # All should succeed
    for resp in responses:
        assert resp.status_code == 200
    
    # Verify all were created
    resp = await client.get("/servers", headers=auth_header())
    servers = resp.json()
    concurrent_servers = [s for s in servers if s["hostname"].startswith("concurrent-server-")]
    assert len(concurrent_servers) == 5
    
    # Cleanup
    for server in concurrent_servers:
        await client.delete(f"/servers/{server['id']}", headers=auth_header())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
