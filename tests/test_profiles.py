"""Tests for profile API endpoints."""

from fastapi.testclient import TestClient


class TestProfileEndpoints:
    """Tests for /api/profiles endpoints."""

    def test_list_profiles_empty(self, client: TestClient) -> None:
        """Test listing profiles when none exist."""
        response = client.get("/api/profiles")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_profile(
        self,
        client: TestClient,
        sample_machine: dict,
        sample_plate: dict,
        sample_filament: dict,
    ) -> None:
        """Test creating a new profile."""
        response = client.post(
            "/api/profiles",
            json={
                "filament_id": sample_filament["id"],
                "machine_id": sample_machine["id"],
                "plate_id": sample_plate["id"],
                "nozzle_temp": 210,
                "bed_temp": 60,
                "flow_ratio": 0.98,
                "pressure_advance": 0.035,
                "max_volumetric_speed": 15.0,
                "retraction_length": 0.8,
                "retraction_speed": 30.0,
                "fan_min_speed": 35,
                "fan_max_speed": 100,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nozzle_temp"] == 210
        assert data["bed_temp"] == 60
        assert data["flow_ratio"] == 0.98
        assert data["pressure_advance"] == 0.035

    def test_create_profile_invalid_filament(
        self, client: TestClient, sample_machine: dict, sample_plate: dict
    ) -> None:
        """Test creating profile with invalid filament ID."""
        response = client.post(
            "/api/profiles",
            json={
                "filament_id": 999,
                "machine_id": sample_machine["id"],
                "plate_id": sample_plate["id"],
                "nozzle_temp": 200,
                "bed_temp": 60,
            },
        )
        assert response.status_code == 404
        assert "Filament" in response.json()["detail"]

    def test_create_profile_invalid_machine(
        self, client: TestClient, sample_plate: dict, sample_filament: dict
    ) -> None:
        """Test creating profile with invalid machine ID."""
        response = client.post(
            "/api/profiles",
            json={
                "filament_id": sample_filament["id"],
                "machine_id": 999,
                "plate_id": sample_plate["id"],
                "nozzle_temp": 200,
                "bed_temp": 60,
            },
        )
        assert response.status_code == 404
        assert "Machine" in response.json()["detail"]

    def test_create_profile_duplicate(self, client: TestClient, sample_profile: dict) -> None:
        """Test that duplicate profile combinations are rejected."""
        response = client.post(
            "/api/profiles",
            json={
                "filament_id": sample_profile["filament_id"],
                "machine_id": sample_profile["machine_id"],
                "plate_id": sample_profile["plate_id"],
                "nozzle_temp": 200,
                "bed_temp": 60,
            },
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_get_profile(self, client: TestClient, sample_profile: dict) -> None:
        """Test getting a profile by ID."""
        response = client.get(f"/api/profiles/{sample_profile['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["nozzle_temp"] == sample_profile["nozzle_temp"]
        # Should include related entities
        assert "filament" in data
        assert "machine" in data
        assert "plate" in data

    def test_get_profile_not_found(self, client: TestClient) -> None:
        """Test getting a non-existent profile."""
        response = client.get("/api/profiles/999")
        assert response.status_code == 404

    def test_update_profile(self, client: TestClient, sample_profile: dict) -> None:
        """Test updating a profile."""
        response = client.put(
            f"/api/profiles/{sample_profile['id']}",
            json={
                "nozzle_temp": 215,
                "pressure_advance": 0.05,
                "notes": "Updated settings",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nozzle_temp"] == 215
        assert data["pressure_advance"] == 0.05
        assert data["notes"] == "Updated settings"

    def test_delete_profile(self, client: TestClient, sample_profile: dict) -> None:
        """Test deleting a profile."""
        response = client.delete(f"/api/profiles/{sample_profile['id']}")
        assert response.status_code == 204

        response = client.get(f"/api/profiles/{sample_profile['id']}")
        assert response.status_code == 404

    def test_clone_profile(
        self, client: TestClient, sample_profile: dict, sample_plate: dict
    ) -> None:
        """Test cloning a profile to a new plate."""
        # Create another plate
        new_plate = client.post("/api/plates", json={"name": "Smooth PEI"}).json()

        response = client.post(
            f"/api/profiles/{sample_profile['id']}/clone",
            json={"plate_id": new_plate["id"]},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["plate_id"] == new_plate["id"]
        assert data["filament_id"] == sample_profile["filament_id"]
        assert data["machine_id"] == sample_profile["machine_id"]
        assert data["nozzle_temp"] == sample_profile["nozzle_temp"]
        assert data["source"] == "cloned"

    def test_clone_profile_duplicate(self, client: TestClient, sample_profile: dict) -> None:
        """Test that cloning to same combination fails."""
        response = client.post(
            f"/api/profiles/{sample_profile['id']}/clone",
            json={},  # Same machine and plate
        )
        assert response.status_code == 400

    def test_filter_profiles_by_machine(
        self,
        client: TestClient,
        sample_profile: dict,
        sample_filament: dict,
        sample_plate: dict,
    ) -> None:
        """Test filtering profiles by machine."""
        # Create another machine and profile
        machine2 = client.post("/api/machines", json={"name": "Printer 2"}).json()
        client.post(
            "/api/profiles",
            json={
                "filament_id": sample_filament["id"],
                "machine_id": machine2["id"],
                "plate_id": sample_plate["id"],
                "nozzle_temp": 200,
                "bed_temp": 60,
            },
        )

        response = client.get(f"/api/profiles?machine_id={sample_profile['machine_id']}")
        assert response.status_code == 200
        profiles = response.json()
        assert len(profiles) == 1
        assert profiles[0]["machine_id"] == sample_profile["machine_id"]
