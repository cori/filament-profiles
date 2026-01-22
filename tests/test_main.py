"""Tests for main application endpoints."""

from fastapi.testclient import TestClient


class TestMainEndpoints:
    """Tests for root and health endpoints."""

    def test_root(self, client: TestClient) -> None:
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "FilamentProfiles"
        assert "version" in data

    def test_health(self, client: TestClient) -> None:
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
