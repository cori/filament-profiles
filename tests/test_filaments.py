"""Tests for filament API endpoints."""

from fastapi.testclient import TestClient


class TestFilamentEndpoints:
    """Tests for /api/filaments endpoints."""

    def test_list_filaments_empty(self, client: TestClient) -> None:
        """Test listing filaments when none exist."""
        response = client.get("/api/filaments")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_filament(self, client: TestClient) -> None:
        """Test creating a new filament."""
        response = client.post(
            "/api/filaments",
            json={
                "vendor": "Polymaker",
                "material": "PETG",
                "name": "PolyLite",
                "color_name": "Black",
                "color_hex": "#000000",
                "density": 1.27,
                "diameter": 1.75,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["vendor"] == "Polymaker"
        assert data["material"] == "PETG"
        assert data["name"] == "PolyLite"
        assert data["density"] == 1.27

    def test_create_filament_minimal(self, client: TestClient) -> None:
        """Test creating a filament with minimal fields."""
        response = client.post(
            "/api/filaments",
            json={"vendor": "Generic", "material": "PLA", "name": "Basic"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["diameter"] == 1.75  # Default value

    def test_create_filament_with_spoolman_id(self, client: TestClient) -> None:
        """Test creating a filament linked to Spoolman."""
        response = client.post(
            "/api/filaments",
            json={
                "vendor": "Bambu Lab",
                "material": "PLA",
                "name": "Basic",
                "spoolman_filament_id": 42,
            },
        )
        assert response.status_code == 201
        assert response.json()["spoolman_filament_id"] == 42

    def test_get_filament(self, client: TestClient, sample_filament: dict) -> None:
        """Test getting a filament by ID."""
        response = client.get(f"/api/filaments/{sample_filament['id']}")
        assert response.status_code == 200
        assert response.json()["vendor"] == sample_filament["vendor"]

    def test_get_filament_not_found(self, client: TestClient) -> None:
        """Test getting a non-existent filament."""
        response = client.get("/api/filaments/999")
        assert response.status_code == 404

    def test_update_filament(self, client: TestClient, sample_filament: dict) -> None:
        """Test updating a filament."""
        response = client.put(
            f"/api/filaments/{sample_filament['id']}",
            json={"color_name": "New Color", "density": 1.30},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["color_name"] == "New Color"
        assert data["density"] == 1.30

    def test_delete_filament(self, client: TestClient, sample_filament: dict) -> None:
        """Test deleting a filament."""
        response = client.delete(f"/api/filaments/{sample_filament['id']}")
        assert response.status_code == 204

        response = client.get(f"/api/filaments/{sample_filament['id']}")
        assert response.status_code == 404

    def test_filter_filaments_by_vendor(self, client: TestClient) -> None:
        """Test filtering filaments by vendor."""
        client.post(
            "/api/filaments",
            json={"vendor": "Bambu Lab", "material": "PLA", "name": "Basic"},
        )
        client.post(
            "/api/filaments",
            json={"vendor": "Polymaker", "material": "PLA", "name": "PolyLite"},
        )

        response = client.get("/api/filaments?vendor=bambu")
        assert response.status_code == 200
        filaments = response.json()
        assert len(filaments) == 1
        assert filaments[0]["vendor"] == "Bambu Lab"

    def test_filter_filaments_by_material(self, client: TestClient) -> None:
        """Test filtering filaments by material."""
        client.post(
            "/api/filaments",
            json={"vendor": "Generic", "material": "PLA", "name": "PLA"},
        )
        client.post(
            "/api/filaments",
            json={"vendor": "Generic", "material": "PETG", "name": "PETG"},
        )

        response = client.get("/api/filaments?material=petg")
        assert response.status_code == 200
        filaments = response.json()
        assert len(filaments) == 1
        assert filaments[0]["material"] == "PETG"
