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

    def test_delete_machine_with_profiles(
        self,
        client: TestClient,
        sample_machine: dict,
        sample_plate: dict,
        sample_filament: dict,
    ) -> None:
        """Test deleting a machine that has profiles should fail."""
        # Create a profile using this machine
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

        # Try to delete the machine
        response = client.delete(f"/api/machines/{sample_machine['id']}")
        assert response.status_code == 409
        assert "profile" in response.json()["detail"].lower()

    def test_bulk_delete_machines(self, client: TestClient) -> None:
        """Test bulk deleting machines."""
        machine1 = client.post("/api/machines", json={"name": "Printer 1"}).json()
        machine2 = client.post("/api/machines", json={"name": "Printer 2"}).json()

        response = client.post(
            "/api/machines/bulk-delete",
            json={"ids": [machine1["id"], machine2["id"]]},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["deleted"]) == 2
        assert len(data["failed"]) == 0

    def test_bulk_delete_machines_with_profiles(
        self,
        client: TestClient,
        sample_machine: dict,
        sample_plate: dict,
        sample_filament: dict,
    ) -> None:
        """Test bulk delete where some machines have profiles."""
        # Create another machine without profiles
        machine2 = client.post("/api/machines", json={"name": "Printer 2"}).json()

        # Create a profile using sample_machine
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
            "/api/machines/bulk-delete",
            json={"ids": [sample_machine["id"], machine2["id"]]},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["deleted"]) == 1
        assert machine2["id"] in data["deleted"]
        assert len(data["failed"]) == 1
        assert data["failed"][0]["id"] == sample_machine["id"]
