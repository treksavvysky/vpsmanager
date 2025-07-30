import main
from fastapi.testclient import TestClient

client = TestClient(main.app)


def test_healthz_all_ok(monkeypatch):
    def mock_ping(hostname):
        return True

    monkeypatch.setattr(main, "ping_vps", mock_ping)
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    for name in main.servers.keys():
        assert data["hosts"][name]["reachable"] is True
