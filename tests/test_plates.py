"""Tests for plate API endpoints."""

from fastapi.testclient import TestClient


class TestPlateEndpoints:
    """Tests for /api/plates endpoints."""

    def test_list_plates_empty(self, client: TestClient) -> None:
        """Test listing plates when none exist."""
        response = client.get("/api/plates")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_plate(self, client: TestClient) -> None:
        """Test creating a new plate."""
        response = client.post(
            "/api/plates",
            json={"name": "Smooth PEI", "description": "Good for PETG"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Smooth PEI"
        assert data["slug"] == "smooth-pei"
        assert data["description"] == "Good for PETG"

    def test_create_plate_duplicate_slug(self, client: TestClient) -> None:
        """Test that duplicate slugs are rejected."""
        client.post("/api/plates", json={"name": "PEI"})
        response = client.post("/api/plates", json={"name": "PEI"})
        assert response.status_code == 400

    def test_get_plate(self, client: TestClient, sample_plate: dict) -> None:
        """Test getting a plate by ID."""
        response = client.get(f"/api/plates/{sample_plate['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == sample_plate["name"]

    def test_get_plate_not_found(self, client: TestClient) -> None:
        """Test getting a non-existent plate."""
        response = client.get("/api/plates/999")
        assert response.status_code == 404

    def test_update_plate(self, client: TestClient, sample_plate: dict) -> None:
        """Test updating a plate."""
        response = client.put(
            f"/api/plates/{sample_plate['id']}",
            json={"name": "Updated Plate", "description": "New description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Plate"
        assert data["description"] == "New description"

    def test_delete_plate(self, client: TestClient, sample_plate: dict) -> None:
        """Test deleting a plate."""
        response = client.delete(f"/api/plates/{sample_plate['id']}")
        assert response.status_code == 204

        response = client.get(f"/api/plates/{sample_plate['id']}")
        assert response.status_code == 404
