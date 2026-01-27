"""Plate API endpoints."""

from fastapi import APIRouter, Body, Depends, HTTPException
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session

from filamentprofiles.database import get_db
from filamentprofiles.models import Plate, Profile
from filamentprofiles.schemas import PlateCreate, PlateResponse, PlateUpdate

router = APIRouter()


@router.get("", response_model=list[PlateResponse])
def list_plates(db: Session = Depends(get_db)) -> list[Plate]:
    """List all plates."""
    result = db.execute(select(Plate).order_by(Plate.name))
    return list(result.scalars().all())


@router.post("", response_model=PlateResponse, status_code=201)
def create_plate(data: PlateCreate, db: Session = Depends(get_db)) -> Plate:
    """Create a new plate."""
    slug = data.slug or slugify(data.name)

    # Check for duplicate slug
    existing = db.execute(select(Plate).where(Plate.slug == slug)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail=f"Plate with slug '{slug}' already exists")

    plate = Plate(
        name=data.name,
        slug=slug,
        description=data.description,
    )
    db.add(plate)
    db.commit()
    db.refresh(plate)
    return plate


@router.get("/{plate_id}", response_model=PlateResponse)
def get_plate(plate_id: int, db: Session = Depends(get_db)) -> Plate:
    """Get a plate by ID."""
    plate = db.get(Plate, plate_id)
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")
    return plate


@router.put("/{plate_id}", response_model=PlateResponse)
def update_plate(plate_id: int, data: PlateUpdate, db: Session = Depends(get_db)) -> Plate:
    """Update a plate."""
    plate = db.get(Plate, plate_id)
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")

    if data.name is not None:
        plate.name = data.name
    if data.slug is not None:
        # Check for duplicate slug
        existing = db.execute(
            select(Plate).where(Plate.slug == data.slug, Plate.id != plate_id)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=400, detail=f"Plate with slug '{data.slug}' already exists"
            )
        plate.slug = data.slug
    if data.description is not None:
        plate.description = data.description

    db.commit()
    db.refresh(plate)
    return plate


@router.delete("/{plate_id}", status_code=204)
def delete_plate(plate_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a plate."""
    plate = db.get(Plate, plate_id)
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")

    # Check for dependent profiles
    profile_count = db.execute(
        select(Profile).where(Profile.plate_id == plate_id)
    ).scalars().all()
    if profile_count:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete plate: {len(profile_count)} profile(s) depend on it. Delete those profiles first.",
        )

    db.delete(plate)
    db.commit()


@router.post("/bulk-delete", status_code=200)
def bulk_delete_plates(
    ids: list[int] = Body(..., embed=True), db: Session = Depends(get_db)
) -> dict:
    """Delete multiple plates. Returns results for each ID."""
    results = {"deleted": [], "failed": []}

    for plate_id in ids:
        plate = db.get(Plate, plate_id)
        if not plate:
            results["failed"].append({"id": plate_id, "error": "Plate not found"})
            continue

        # Check for dependent profiles
        profiles = db.execute(
            select(Profile).where(Profile.plate_id == plate_id)
        ).scalars().all()
        if profiles:
            results["failed"].append({
                "id": plate_id,
                "error": f"{len(profiles)} profile(s) depend on this plate",
            })
            continue

        db.delete(plate)
        results["deleted"].append(plate_id)

    db.commit()
    return results
