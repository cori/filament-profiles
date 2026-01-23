"""Tests for export API endpoints."""

from fastapi.testclient import TestClient


class TestExportEndpoints:
    """Tests for /api/export endpoints."""

    def test_export_profile(self, client: TestClient, sample_profile: dict) -> None:
        """Test exporting a single profile as OrcaSlicer JSON."""
        response = client.get(f"/api/export/profile/{sample_profile['id']}")
        assert response.status_code == 200

        data = response.json()
        assert data["type"] == "filament"
        assert "Bambu Lab" in data["name"]
        assert "PLA" in data["name"]
        assert data["filament_vendor"] == "Bambu Lab"
        assert data["filament_type"] == "PLA"
        assert data["nozzle_temperature"] == ["200"]
        assert data["bed_temperature"] == ["35"]
        assert data["filament_flow_ratio"] == ["0.95"]
        assert data["pressure_advance"] == ["0.04"]
        assert "inherits" in data
        assert "version" in data

    def test_export_profile_not_found(self, client: TestClient) -> None:
        """Test exporting a non-existent profile."""
        response = client.get("/api/export/profile/999")
        assert response.status_code == 404

    def test_export_profile_has_download_header(
        self, client: TestClient, sample_profile: dict
    ) -> None:
        """Test that export includes Content-Disposition header."""
        response = client.get(f"/api/export/profile/{sample_profile['id']}")
        assert "Content-Disposition" in response.headers
        assert "attachment" in response.headers["Content-Disposition"]
        assert ".json" in response.headers["Content-Disposition"]

    def test_export_machine_profiles(
        self,
        client: TestClient,
        sample_profile: dict,
        sample_machine: dict,
        sample_filament: dict,
    ) -> None:
        """Test exporting all profiles for a machine."""
        # Create another plate and profile for the same machine
        plate2 = client.post("/api/plates", json={"name": "G10"}).json()
        client.post(
            "/api/profiles",
            json={
                "filament_id": sample_filament["id"],
                "machine_id": sample_machine["id"],
                "plate_id": plate2["id"],
                "nozzle_temp": 205,
                "bed_temp": 40,
            },
        )

        response = client.get(f"/api/export/machine/{sample_machine['id']}")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_export_machine_not_found(self, client: TestClient) -> None:
        """Test exporting from a non-existent machine."""
        response = client.get("/api/export/machine/999")
        assert response.status_code == 404

    def test_export_machine_no_profiles(
        self, client: TestClient, sample_machine: dict
    ) -> None:
        """Test exporting from a machine with no profiles."""
        # Create a machine with no profiles
        machine = client.post("/api/machines", json={"name": "Empty Printer"}).json()
        response = client.get(f"/api/export/machine/{machine['id']}")
        assert response.status_code == 404
        assert "No profiles found" in response.json()["detail"]

    def test_preview_profile(self, client: TestClient, sample_profile: dict) -> None:
        """Test previewing a profile without download header."""
        response = client.get(f"/api/export/profile/{sample_profile['id']}/preview")
        assert response.status_code == 200
        assert "Content-Disposition" not in response.headers

        data = response.json()
        assert data["type"] == "filament"

    def test_export_profile_with_color(self, client: TestClient, sample_profile: dict) -> None:
        """Test that color is included in export."""
        response = client.get(f"/api/export/profile/{sample_profile['id']}")
        data = response.json()
        assert "filament_colour" in data
        assert data["filament_colour"] == ["#E8E0D5"]

    def test_export_profile_inherits_correct_base(self, client: TestClient) -> None:
        """Test that material type maps to correct OrcaSlicer base."""
        # Create PETG filament
        filament = client.post(
            "/api/filaments",
            json={"vendor": "Test", "material": "PETG", "name": "Test"},
        ).json()
        machine = client.post("/api/machines", json={"name": "Printer"}).json()
        plate = client.post("/api/plates", json={"name": "PEI"}).json()
        profile = client.post(
            "/api/profiles",
            json={
                "filament_id": filament["id"],
                "machine_id": machine["id"],
                "plate_id": plate["id"],
                "nozzle_temp": 240,
                "bed_temp": 80,
            },
        ).json()

        response = client.get(f"/api/export/profile/{profile['id']}")
        data = response.json()
        assert data["inherits"] == "Generic PETG"
