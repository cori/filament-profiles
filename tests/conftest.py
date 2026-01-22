"""Pytest fixtures for FilamentProfiles tests."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from filamentprofiles.database import get_db
from filamentprofiles.main import app
from filamentprofiles.models import Base

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database override."""

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_machine(client: TestClient) -> dict:
    """Create a sample machine for tests."""
    response = client.post(
        "/api/machines",
        json={"name": "QIDI Plus4", "nozzle_diameter": 0.4},
    )
    return response.json()


@pytest.fixture
def sample_plate(client: TestClient) -> dict:
    """Create a sample plate for tests."""
    response = client.post(
        "/api/plates",
        json={"name": "Textured PEI"},
    )
    return response.json()


@pytest.fixture
def sample_filament(client: TestClient) -> dict:
    """Create a sample filament for tests."""
    response = client.post(
        "/api/filaments",
        json={
            "vendor": "Bambu Lab",
            "material": "PLA",
            "name": "Matte",
            "color_name": "Bone White",
            "color_hex": "#E8E0D5",
            "density": 1.24,
            "diameter": 1.75,
        },
    )
    return response.json()


@pytest.fixture
def sample_profile(
    client: TestClient, sample_machine: dict, sample_plate: dict, sample_filament: dict
) -> dict:
    """Create a sample profile for tests."""
    response = client.post(
        "/api/profiles",
        json={
            "filament_id": sample_filament["id"],
            "machine_id": sample_machine["id"],
            "plate_id": sample_plate["id"],
            "nozzle_temp": 200,
            "bed_temp": 35,
            "flow_ratio": 0.95,
            "pressure_advance": 0.04,
        },
    )
    return response.json()
