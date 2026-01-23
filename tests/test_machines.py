"""Tests for machine API endpoints."""

from fastapi.testclient import TestClient


class TestMachineEndpoints:
    """Tests for /api/machines endpoints."""

    def test_list_machines_empty(self, client: TestClient) -> None:
        """Test listing machines when none exist."""
        response = client.get("/api/machines")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_machine(self, client: TestClient) -> None:
        """Test creating a new machine."""
        response = client.post(
            "/api/machines",
            json={"name": "Voron 2.4", "nozzle_diameter": 0.4},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Voron 2.4"
        assert data["slug"] == "voron-2-4"
        assert data["nozzle_diameter"] == 0.4
        assert "id" in data
        assert "created_at" in data

    def test_create_machine_with_custom_slug(self, client: TestClient) -> None:
        """Test creating a machine with custom slug."""
        response = client.post(
            "/api/machines",
            json={"name": "My Printer", "slug": "custom-slug", "nozzle_diameter": 0.6},
        )
        assert response.status_code == 201
        assert response.json()["slug"] == "custom-slug"

    def test_create_machine_duplicate_slug(self, client: TestClient) -> None:
        """Test that duplicate slugs are rejected."""
        client.post("/api/machines", json={"name": "Printer 1"})
        response = client.post("/api/machines", json={"name": "Printer 1"})
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_get_machine(self, client: TestClient, sample_machine: dict) -> None:
        """Test getting a machine by ID."""
        response = client.get(f"/api/machines/{sample_machine['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == sample_machine["name"]

    def test_get_machine_not_found(self, client: TestClient) -> None:
        """Test getting a non-existent machine."""
        response = client.get("/api/machines/999")
        assert response.status_code == 404

    def test_update_machine(self, client: TestClient, sample_machine: dict) -> None:
        """Test updating a machine."""
        response = client.put(
            f"/api/machines/{sample_machine['id']}",
            json={"name": "Updated Name", "nozzle_diameter": 0.6},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["nozzle_diameter"] == 0.6

    def test_delete_machine(self, client: TestClient, sample_machine: dict) -> None:
        """Test deleting a machine."""
        response = client.delete(f"/api/machines/{sample_machine['id']}")
        assert response.status_code == 204

        # Verify it's gone
        response = client.get(f"/api/machines/{sample_machine['id']}")
        assert response.status_code == 404

    def test_list_machines(self, client: TestClient) -> None:
        """Test listing multiple machines."""
        client.post("/api/machines", json={"name": "Printer A"})
        client.post("/api/machines", json={"name": "Printer B"})

        response = client.get("/api/machines")
        assert response.status_code == 200
        machines = response.json()
        assert len(machines) == 2
