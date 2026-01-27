"""Profile API endpoints."""

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from filamentprofiles.database import get_db
from filamentprofiles.models import Filament, Machine, Plate, Profile
from filamentprofiles.schemas.profile import (
    ProfileClone,
    ProfileCreate,
    ProfileDetailResponse,
    ProfileResponse,
    ProfileUpdate,
)

router = APIRouter()


@router.get("", response_model=list[ProfileDetailResponse])
def list_profiles(
    filament_id: int | None = Query(None, description="Filter by filament ID"),
    machine_id: int | None = Query(None, description="Filter by machine ID"),
    plate_id: int | None = Query(None, description="Filter by plate ID"),
    db: Session = Depends(get_db),
) -> list[Profile]:
    """List profiles with optional filtering."""
    query = (
        select(Profile)
        .options(
            joinedload(Profile.filament),
            joinedload(Profile.machine),
            joinedload(Profile.plate),
        )
    )

    if filament_id:
        query = query.where(Profile.filament_id == filament_id)
    if machine_id:
        query = query.where(Profile.machine_id == machine_id)
    if plate_id:
        query = query.where(Profile.plate_id == plate_id)

    result = db.execute(query)
    return list(result.scalars().unique().all())


@router.post("", response_model=ProfileResponse, status_code=201)
def create_profile(data: ProfileCreate, db: Session = Depends(get_db)) -> Profile:
    """Create a new profile."""
    # Verify foreign keys exist
    if not db.get(Filament, data.filament_id):
        raise HTTPException(status_code=404, detail="Filament not found")
    if not db.get(Machine, data.machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    if not db.get(Plate, data.plate_id):
        raise HTTPException(status_code=404, detail="Plate not found")

    profile = Profile(
        filament_id=data.filament_id,
        machine_id=data.machine_id,
        plate_id=data.plate_id,
        nozzle_temp=data.nozzle_temp,
        nozzle_temp_first_layer=data.nozzle_temp_first_layer,
        bed_temp=data.bed_temp,
        bed_temp_first_layer=data.bed_temp_first_layer,
        chamber_temp=data.chamber_temp,
        flow_ratio=data.flow_ratio,
        pressure_advance=data.pressure_advance,
        max_volumetric_speed=data.max_volumetric_speed,
        retraction_length=data.retraction_length,
        retraction_speed=data.retraction_speed,
        print_speed=data.print_speed,
        first_layer_speed=data.first_layer_speed,
        outer_wall_speed=data.outer_wall_speed,
        inner_wall_speed=data.inner_wall_speed,
        infill_speed=data.infill_speed,
        travel_speed=data.travel_speed,
        fan_min_speed=data.fan_min_speed,
        fan_max_speed=data.fan_max_speed,
        disable_fan_first_layers=data.disable_fan_first_layers,
        is_default=data.is_default,
        notes=data.notes,
        source=data.source,
        source_profile=data.source_profile,
    )

    try:
        db.add(profile)
        db.commit()
        db.refresh(profile)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="A profile for this filament/machine/plate combination already exists",
        )

    return profile


@router.get("/{profile_id}", response_model=ProfileDetailResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)) -> Profile:
    """Get a profile by ID with related entities."""
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
    return profile


@router.put("/{profile_id}", response_model=ProfileResponse)
def update_profile(
    profile_id: int, data: ProfileUpdate, db: Session = Depends(get_db)
) -> Profile:
    """Update a profile."""
    profile = db.get(Profile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update temperature settings
    if data.nozzle_temp is not None:
        profile.nozzle_temp = data.nozzle_temp
    if data.nozzle_temp_first_layer is not None:
        profile.nozzle_temp_first_layer = data.nozzle_temp_first_layer
    if data.bed_temp is not None:
        profile.bed_temp = data.bed_temp
    if data.bed_temp_first_layer is not None:
        profile.bed_temp_first_layer = data.bed_temp_first_layer
    if data.chamber_temp is not None:
        profile.chamber_temp = data.chamber_temp

    # Update flow and extrusion
    if data.flow_ratio is not None:
        profile.flow_ratio = data.flow_ratio
    if data.pressure_advance is not None:
        profile.pressure_advance = data.pressure_advance
    if data.max_volumetric_speed is not None:
        profile.max_volumetric_speed = data.max_volumetric_speed

    # Update retraction
    if data.retraction_length is not None:
        profile.retraction_length = data.retraction_length
    if data.retraction_speed is not None:
        profile.retraction_speed = data.retraction_speed

    # Update speeds
    if data.print_speed is not None:
        profile.print_speed = data.print_speed
    if data.first_layer_speed is not None:
        profile.first_layer_speed = data.first_layer_speed
    if data.outer_wall_speed is not None:
        profile.outer_wall_speed = data.outer_wall_speed
    if data.inner_wall_speed is not None:
        profile.inner_wall_speed = data.inner_wall_speed
    if data.infill_speed is not None:
        profile.infill_speed = data.infill_speed
    if data.travel_speed is not None:
        profile.travel_speed = data.travel_speed

    # Update cooling
    if data.fan_min_speed is not None:
        profile.fan_min_speed = data.fan_min_speed
    if data.fan_max_speed is not None:
        profile.fan_max_speed = data.fan_max_speed
    if data.disable_fan_first_layers is not None:
        profile.disable_fan_first_layers = data.disable_fan_first_layers

    # Update metadata
    if data.is_default is not None:
        profile.is_default = data.is_default
    if data.notes is not None:
        profile.notes = data.notes

    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{profile_id}", status_code=204)
def delete_profile(profile_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a profile."""
    profile = db.get(Profile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(profile)
    db.commit()


@router.post("/bulk-delete", status_code=200)
def bulk_delete_profiles(
    ids: list[int] = Body(..., embed=True), db: Session = Depends(get_db)
) -> dict:
    """Delete multiple profiles. Returns results for each ID."""
    results = {"deleted": [], "failed": []}

    for profile_id in ids:
        profile = db.get(Profile, profile_id)
        if not profile:
            results["failed"].append({"id": profile_id, "error": "Profile not found"})
            continue

        db.delete(profile)
        results["deleted"].append(profile_id)

    db.commit()
    return results


@router.post("/{profile_id}/clone", response_model=ProfileResponse, status_code=201)
def clone_profile(
    profile_id: int, data: ProfileClone, db: Session = Depends(get_db)
) -> Profile:
    """Clone a profile to a new machine/plate combination."""
    original = db.get(Profile, profile_id)
    if not original:
        raise HTTPException(status_code=404, detail="Profile not found")

    machine_id = data.machine_id or original.machine_id
    plate_id = data.plate_id or original.plate_id

    # Verify the new machine/plate exist
    if data.machine_id and not db.get(Machine, data.machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    if data.plate_id and not db.get(Plate, data.plate_id):
        raise HTTPException(status_code=404, detail="Plate not found")

    # Create the clone
    clone = Profile(
        filament_id=original.filament_id,
        machine_id=machine_id,
        plate_id=plate_id,
        nozzle_temp=original.nozzle_temp,
        nozzle_temp_first_layer=original.nozzle_temp_first_layer,
        bed_temp=original.bed_temp,
        bed_temp_first_layer=original.bed_temp_first_layer,
        chamber_temp=original.chamber_temp,
        flow_ratio=original.flow_ratio,
        pressure_advance=original.pressure_advance,
        max_volumetric_speed=original.max_volumetric_speed,
        retraction_length=original.retraction_length,
        retraction_speed=original.retraction_speed,
        print_speed=original.print_speed,
        first_layer_speed=original.first_layer_speed,
        outer_wall_speed=original.outer_wall_speed,
        inner_wall_speed=original.inner_wall_speed,
        infill_speed=original.infill_speed,
        travel_speed=original.travel_speed,
        fan_min_speed=original.fan_min_speed,
        fan_max_speed=original.fan_max_speed,
        disable_fan_first_layers=original.disable_fan_first_layers,
        is_default=False,  # Clone is never default
        notes=original.notes,
        source="cloned",
        source_profile=f"profile:{original.id}",
    )

    try:
        db.add(clone)
        db.commit()
        db.refresh(clone)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="A profile for this filament/machine/plate combination already exists",
        )

    return clone
