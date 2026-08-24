from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_response_shape():
    response = client.get("/health")
    body = response.json()
    assert set(body.keys()) == {"status", "service", "database"}
    assert body["status"] == "healthy"
    assert body["database"] in {"connected", "disconnected"}


def test_health_endpoint_available_under_api_v1_prefix():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
