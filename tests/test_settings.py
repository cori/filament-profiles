"""Tests for settings API endpoints."""

from fastapi.testclient import TestClient


class TestSettingsEndpoints:
    """Tests for /api/settings endpoints."""

    def test_get_settings(self, client: TestClient) -> None:
        """Test getting settings."""
        response = client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert "spoolman_url" in data
        assert "spoolman_connected" in data

    def test_spoolman_status_no_url(self, client: TestClient) -> None:
        """Test Spoolman status when URL is not configured."""
        response = client.get("/api/settings/spoolman/status")
        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is False
        assert "not configured" in data["error"].lower()

    def test_spoolman_filaments_no_url(self, client: TestClient) -> None:
        """Test getting Spoolman filaments when URL is not configured."""
        response = client.get("/api/settings/spoolman/filaments")
        assert response.status_code == 400
        assert "not configured" in response.json()["detail"].lower()
