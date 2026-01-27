"""Filament API endpoints."""

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from filamentprofiles.database import get_db
from filamentprofiles.models import Filament, Profile
from filamentprofiles.schemas import FilamentCreate, FilamentResponse, FilamentUpdate

router = APIRouter()


@router.get("", response_model=list[FilamentResponse])
def list_filaments(
    vendor: str | None = Query(None, description="Filter by vendor"),
    material: str | None = Query(None, description="Filter by material type"),
    db: Session = Depends(get_db),
) -> list[Filament]:
    """List all filaments with optional filtering."""
    query = select(Filament)

    if vendor:
        query = query.where(Filament.vendor.ilike(f"%{vendor}%"))
    if material:
        query = query.where(Filament.material.ilike(f"%{material}%"))

    query = query.order_by(Filament.vendor, Filament.material, Filament.name)
    result = db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=FilamentResponse, status_code=201)
def create_filament(data: FilamentCreate, db: Session = Depends(get_db)) -> Filament:
    """Create a new filament."""
    filament = Filament(
        vendor=data.vendor,
        material=data.material,
        name=data.name,
        color_name=data.color_name,
        color_hex=data.color_hex,
        density=data.density,
        diameter=data.diameter,
        spoolman_filament_id=data.spoolman_filament_id,
    )
    db.add(filament)
    db.commit()
    db.refresh(filament)
    return filament


@router.get("/{filament_id}", response_model=FilamentResponse)
def get_filament(filament_id: int, db: Session = Depends(get_db)) -> Filament:
    """Get a filament by ID."""
    filament = db.get(Filament, filament_id)
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    return filament


@router.put("/{filament_id}", response_model=FilamentResponse)
def update_filament(
    filament_id: int, data: FilamentUpdate, db: Session = Depends(get_db)
) -> Filament:
    """Update a filament."""
    filament = db.get(Filament, filament_id)
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")

    if data.vendor is not None:
        filament.vendor = data.vendor
    if data.material is not None:
        filament.material = data.material
    if data.name is not None:
        filament.name = data.name
    if data.color_name is not None:
        filament.color_name = data.color_name
    if data.color_hex is not None:
        filament.color_hex = data.color_hex
    if data.density is not None:
        filament.density = data.density
    if data.diameter is not None:
        filament.diameter = data.diameter
    if data.spoolman_filament_id is not None:
        filament.spoolman_filament_id = data.spoolman_filament_id

    db.commit()
    db.refresh(filament)
    return filament


@router.delete("/{filament_id}", status_code=204)
def delete_filament(filament_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a filament."""
    filament = db.get(Filament, filament_id)
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")

    # Check for dependent profiles
    profile_count = db.execute(
        select(Profile).where(Profile.filament_id == filament_id)
    ).scalars().all()
    if profile_count:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete filament: {len(profile_count)} profile(s) depend on it. "
            "Delete those profiles first.",
        )

    db.delete(filament)
    db.commit()


@router.post("/bulk-delete", status_code=200)
def bulk_delete_filaments(
    ids: list[int] = Body(..., embed=True), db: Session = Depends(get_db)
) -> dict:
    """Delete multiple filaments. Returns results for each ID."""
    results = {"deleted": [], "failed": []}

    for filament_id in ids:
        filament = db.get(Filament, filament_id)
        if not filament:
            results["failed"].append({"id": filament_id, "error": "Filament not found"})
            continue

        # Check for dependent profiles
        profiles = db.execute(
            select(Profile).where(Profile.filament_id == filament_id)
        ).scalars().all()
        if profiles:
            results["failed"].append({
                "id": filament_id,
                "error": f"{len(profiles)} profile(s) depend on this filament",
            })
            continue

        db.delete(filament)
        results["deleted"].append(filament_id)

    db.commit()
    return results
