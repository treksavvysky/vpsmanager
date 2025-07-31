#!/usr/bin/env python3
"""
Simple test runner for the VPS Manager server tests
"""
import asyncio
import os
import sys
import json

# Set environment variables
os.environ["API_KEY"] = "testkey"

# Add current directory to path
sys.path.insert(0, '.')

from httpx import AsyncClient
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models.server import Server, Provider, Role, Status
from main import app

# Test database setup
DATABASE_URL = "sqlite:///./test_runner.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def setup_test_db():
    """Set up test database with fresh data."""
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

def cleanup_test_db():
    """Clean up test database."""
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides = {}

def auth_header():
    """Helper function to get authentication headers."""
    return {"Authorization": "testkey"}

async def test_authentication_required():
    """Test that API endpoints require authentication."""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # No auth header
        resp = await client.get("/servers")
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
        
        # Invalid auth
        resp = await client.get("/servers", headers={"Authorization": "invalid"})
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        
        # Valid auth should work
        resp = await client.get("/servers", headers=auth_header())
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

async def test_list_servers_basic():
    """Test basic server listing functionality."""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/servers", headers=auth_header())
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        
        # Verify response structure
        server = data[0]
        required_fields = ["id", "hostname", "provider", "public_ip", "role", "status", "tags"]
        for field in required_fields:
            assert field in server, f"Missing field: {field}"

async def test_create_server_valid():
    """Test creating a server with valid data."""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        new_server = {
            "hostname": "new-test-server",
            "provider": "AWS",
            "public_ip": "192.168.1.1",
            "role": "dev",
            "status": "online",
            "tags": {"team": "devops", "project": "alpha"}
        }
        
        resp = await client.post("/servers", json=new_server, headers=auth_header())
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        created = resp.json()
        assert created["hostname"] == new_server["hostname"]
        assert created["provider"] == new_server["provider"]
        assert "id" in created

async def test_create_server_duplicate_ip():
    """Test that creating a server with duplicate IP fails."""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        new_server = {
            "hostname": "duplicate-ip-server",
            "provider": "AWS",
            "public_ip": "10.0.0.1",  # This IP already exists
            "role": "dev"
        }
        
        resp = await client.post("/servers", json=new_server, headers=auth_header())
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
        assert "already exists" in resp.json()["detail"]

async def test_get_server_by_id():
    """Test retrieving a specific server by ID."""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
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

async def test_update_server_role():
    """Test updating a server's role."""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get a server ID
        resp = await client.get("/servers", headers=auth_header())
        server_id = resp.json()[0]["id"]
        
        # Update role
        update_data = {"role": "prod"}
        resp = await client.patch(f"/servers/{server_id}", json=update_data, headers=auth_header())
        assert resp.status_code == 200
        
        updated = resp.json()
        assert updated["role"] == "prod"

async def test_delete_server():
    """Test deleting a server."""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
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

async def test_complete_crud_workflow():
    """Test complete Create, Read, Update, Delete workflow."""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
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
        
        # READ
        resp = await client.get(f"/servers/{server_id}", headers=auth_header())
        assert resp.status_code == 200
        retrieved = resp.json()
        assert retrieved["hostname"] == new_server["hostname"]
        
        # UPDATE
        update_data = {"role": "prod", "status": "maintenance"}
        resp = await client.patch(f"/servers/{server_id}", json=update_data, headers=auth_header())
        assert resp.status_code == 200
        updated = resp.json()
        assert updated["role"] == "prod"
        assert updated["status"] == "maintenance"
        
        # DELETE
        resp = await client.delete(f"/servers/{server_id}", headers=auth_header())
        assert resp.status_code == 204

async def run_test(test_func, test_name):
    """Run a single test function."""
    print(f"\n🔄 Running {test_name}...")
    try:
        await test_func()
        print(f"✅ {test_name} PASSED")
        return True
    except Exception as e:
        print(f"❌ {test_name} FAILED: {str(e)}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting VPS Manager Test Suite")
    print("=" * 50)
    
    # Setup database
    setup_test_db()
    
    try:
        # List of tests to run
        tests = [
            (test_authentication_required, "Authentication Required"),
            (test_list_servers_basic, "List Servers Basic"),
            (test_create_server_valid, "Create Server Valid"),
            (test_create_server_duplicate_ip, "Create Server Duplicate IP"),
            (test_get_server_by_id, "Get Server by ID"),
            (test_update_server_role, "Update Server Role"),
            (test_delete_server, "Delete Server"),
            (test_complete_crud_workflow, "Complete CRUD Workflow"),
        ]
        
        passed = 0
        failed = 0
        
        for test_func, test_name in tests:
            success = await run_test(test_func, test_name)
            if success:
                passed += 1
            else:
                failed += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed!")
            return 0
        else:
            print("💥 Some tests failed!")
            return 1
    
    finally:
        # Cleanup
        cleanup_test_db()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
