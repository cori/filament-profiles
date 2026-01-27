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

    def test_delete_plate_with_profiles(
        self,
        client: TestClient,
        sample_machine: dict,
        sample_plate: dict,
        sample_filament: dict,
    ) -> None:
        """Test deleting a plate that has profiles should fail."""
        # Create a profile using this plate
        client.post(
            "/api/profiles",
            json={
                "filament_id": sample_filament["id"],
                "machine_id": sample_machine["id"],
                "plate_id": sample_plate["id"],
                "nozzle_temp": 200,
                "bed_temp": 60,
            },
        )

        # Try to delete the plate
        response = client.delete(f"/api/plates/{sample_plate['id']}")
        assert response.status_code == 409
        assert "profile" in response.json()["detail"].lower()

    def test_bulk_delete_plates(self, client: TestClient) -> None:
        """Test bulk deleting plates."""
        plate1 = client.post("/api/plates", json={"name": "Plate 1"}).json()
        plate2 = client.post("/api/plates", json={"name": "Plate 2"}).json()

        response = client.post(
            "/api/plates/bulk-delete",
            json={"ids": [plate1["id"], plate2["id"]]},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["deleted"]) == 2
        assert len(data["failed"]) == 0

    def test_bulk_delete_plates_with_profiles(
        self,
        client: TestClient,
        sample_machine: dict,
        sample_plate: dict,
        sample_filament: dict,
    ) -> None:
        """Test bulk delete where some plates have profiles."""
        # Create another plate without profiles
        plate2 = client.post("/api/plates", json={"name": "Plate 2"}).json()

        # Create a profile using sample_plate
        client.post(
            "/api/profiles",
            json={
                "filament_id": sample_filament["id"],
                "machine_id": sample_machine["id"],
                "plate_id": sample_plate["id"],
                "nozzle_temp": 200,
                "bed_temp": 60,
            },
        )

        # Try to bulk delete both
        response = client.post(
            "/api/plates/bulk-delete",
            json={"ids": [sample_plate["id"], plate2["id"]]},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["deleted"]) == 1
        assert plate2["id"] in data["deleted"]
        assert len(data["failed"]) == 1
        assert data["failed"][0]["id"] == sample_plate["id"]
