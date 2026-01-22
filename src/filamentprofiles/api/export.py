"""Export API endpoints for slicer profiles."""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from filamentprofiles.database import get_db
from filamentprofiles.models import Machine, Profile

router = APIRouter()

# OrcaSlicer/QIDI Studio profile version
SLICER_VERSION = "1.9.0.0"


def profile_to_orcaslicer(profile: Profile) -> dict[str, Any]:
    """Convert a profile to OrcaSlicer JSON format."""
    filament = profile.filament
    machine = profile.machine
    plate = profile.plate

    # Build profile name: "{Vendor} {Material} {Name} @{Machine} {Plate}"
    profile_name = f"{filament.vendor} {filament.material} {filament.name} @{machine.name}"
    if plate.name:
        profile_name += f" {plate.name}"

    # Build filament ID (for slicer internal use)
    filament_id = slugify(
        f"user_{filament.vendor}_{filament.material}_{filament.name}",
        separator="_",
    )

    # Map material to OrcaSlicer inherits base
    material_base_map = {
        "PLA": "Generic PLA",
        "PETG": "Generic PETG",
        "ABS": "Generic ABS",
        "ASA": "Generic ASA",
        "TPU": "Generic TPU",
        "PA": "Generic PA",
        "PC": "Generic PC",
        "PVA": "Generic PVA",
        "HIPS": "Generic HIPS",
    }
    inherits = material_base_map.get(filament.material.upper(), f"Generic {filament.material}")

    # Build the JSON structure
    data: dict[str, Any] = {
        "type": "filament",
        "name": profile_name,
        "inherits": inherits,
        "from": "User",
        "filament_id": filament_id,
        "filament_vendor": filament.vendor,
        "filament_type": filament.material,
        "filament_density": str(filament.density) if filament.density else "1.24",
        "filament_diameter": [str(filament.diameter)],
        # Temperature settings (arrays as strings for OrcaSlicer)
        "nozzle_temperature": [str(profile.nozzle_temp)],
        "nozzle_temperature_initial_layer": [
            str(profile.nozzle_temp_first_layer or profile.nozzle_temp)
        ],
        "bed_temperature": [str(profile.bed_temp)],
        "bed_temperature_initial_layer": [
            str(profile.bed_temp_first_layer or profile.bed_temp)
        ],
        # Flow settings
        "filament_flow_ratio": [str(profile.flow_ratio)],
        # Compatible printers
        "compatible_printers": [f"{machine.name} {machine.nozzle_diameter} nozzle"],
        "version": SLICER_VERSION,
    }

    # Add color if available
    if filament.color_hex:
        color = filament.color_hex
        if not color.startswith("#"):
            color = f"#{color}"
        data["filament_colour"] = [color]

    # Optional chamber temp
    if profile.chamber_temp:
        data["chamber_temperature"] = [str(profile.chamber_temp)]

    # Pressure advance
    if profile.pressure_advance is not None:
        data["pressure_advance"] = [str(profile.pressure_advance)]

    # Max volumetric speed
    if profile.max_volumetric_speed is not None:
        data["filament_max_volumetric_speed"] = [str(profile.max_volumetric_speed)]

    # Retraction settings
    if profile.retraction_length is not None:
        data["filament_retraction_length"] = [str(profile.retraction_length)]
    if profile.retraction_speed is not None:
        data["filament_retraction_speed"] = [str(profile.retraction_speed)]

    # Fan settings
    if profile.fan_min_speed is not None:
        data["fan_min_speed"] = [str(profile.fan_min_speed)]
    if profile.fan_max_speed is not None:
        data["fan_max_speed"] = [str(profile.fan_max_speed)]
    if profile.disable_fan_first_layers is not None:
        data["close_fan_the_first_x_layers"] = [str(profile.disable_fan_first_layers)]

    return data


@router.get("/profile/{profile_id}")
def export_profile(profile_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    """Export a single profile as OrcaSlicer JSON."""
    query = (
        select(Profile)
        .options(
            joinedload(Profile.filament),
            joinedload(Profile.machine),
            joinedload(Profile.plate),
        )
        .where(Profile.id == profile_id)
    )
    profile = db.execute(query).scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    data = profile_to_orcaslicer(profile)

    # Build filename
    filename = slugify(data["name"], separator="_") + ".json"

    return JSONResponse(
        content=data,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/machine/{machine_id}")
def export_machine_profiles(machine_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    """Export all profiles for a machine as a JSON array."""
    machine = db.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    query = (
        select(Profile)
        .options(
            joinedload(Profile.filament),
            joinedload(Profile.machine),
            joinedload(Profile.plate),
        )
        .where(Profile.machine_id == machine_id)
    )
    profiles = db.execute(query).scalars().unique().all()

    if not profiles:
        raise HTTPException(
            status_code=404, detail="No profiles found for this machine"
        )

    data = [profile_to_orcaslicer(p) for p in profiles]

    filename = f"{slugify(machine.name)}_profiles.json"

    return JSONResponse(
        content=data,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/profile/{profile_id}/preview")
def preview_profile(profile_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Preview a profile export without downloading."""
    query = (
        select(Profile)
        .options(
            joinedload(Profile.filament),
            joinedload(Profile.machine),
            joinedload(Profile.plate),
        )
        .where(Profile.id == profile_id)
    )
    profile = db.execute(query).scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile_to_orcaslicer(profile)
