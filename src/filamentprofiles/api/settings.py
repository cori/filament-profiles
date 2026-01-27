"""Settings API endpoints."""

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from filamentprofiles.config import settings

router = APIRouter()


class SettingsResponse(BaseModel):
    """Current settings."""

    spoolman_url: str | None
    spoolman_connected: bool = False


class SettingsUpdate(BaseModel):
    """Settings update payload."""

    spoolman_url: str | None = None


class SpoolmanStatus(BaseModel):
    """Spoolman connection status."""

    connected: bool
    version: str | None = None
    error: str | None = None


class SpoolmanFilament(BaseModel):
    """Filament from Spoolman."""

    id: int
    name: str | None
    vendor_name: str | None
    material: str | None
    color_hex: str | None
    density: float | None
    diameter: float | None


@router.get("", response_model=SettingsResponse)
def get_settings() -> SettingsResponse:
    """Get current settings."""
    return SettingsResponse(
        spoolman_url=settings.spoolman_url,
        spoolman_connected=False,  # Will be checked by frontend separately
    )


@router.get("/spoolman/status", response_model=SpoolmanStatus)
async def check_spoolman_status() -> SpoolmanStatus:
    """Check if Spoolman is reachable and get its version."""
    if not settings.spoolman_url:
        return SpoolmanStatus(connected=False, error="Spoolman URL not configured")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.spoolman_url}/api/v1/info")
            if response.status_code == 200:
                data = response.json()
                return SpoolmanStatus(
                    connected=True,
                    version=data.get("version", "unknown"),
                )
            return SpoolmanStatus(
                connected=False,
                error=f"Spoolman returned status {response.status_code}",
            )
    except httpx.TimeoutException:
        return SpoolmanStatus(connected=False, error="Connection timed out")
    except httpx.ConnectError as e:
        return SpoolmanStatus(connected=False, error=f"Connection failed: {str(e)}")
    except Exception as e:
        return SpoolmanStatus(connected=False, error=str(e))


@router.get("/spoolman/filaments", response_model=list[SpoolmanFilament])
async def get_spoolman_filaments() -> list[SpoolmanFilament]:
    """Fetch filaments from Spoolman."""
    if not settings.spoolman_url:
        raise HTTPException(status_code=400, detail="Spoolman URL not configured")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{settings.spoolman_url}/api/v1/filament")
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Spoolman returned status {response.status_code}",
                )

            data = response.json()
            filaments = []
            for item in data:
                vendor = item.get("vendor", {})
                filaments.append(
                    SpoolmanFilament(
                        id=item.get("id"),
                        name=item.get("name"),
                        vendor_name=vendor.get("name") if vendor else None,
                        material=item.get("material"),
                        color_hex=item.get("color_hex"),
                        density=item.get("density"),
                        diameter=item.get("diameter"),
                    )
                )
            return filaments
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Spoolman connection timed out")
    except httpx.ConnectError as e:
        raise HTTPException(status_code=502, detail=f"Cannot connect to Spoolman: {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
