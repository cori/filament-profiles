"""Machine API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session

from filamentprofiles.database import get_db
from filamentprofiles.models import Machine
from filamentprofiles.schemas import MachineCreate, MachineResponse, MachineUpdate

router = APIRouter()


@router.get("", response_model=list[MachineResponse])
def list_machines(db: Session = Depends(get_db)) -> list[Machine]:
    """List all machines."""
    result = db.execute(select(Machine).order_by(Machine.name))
    return list(result.scalars().all())


@router.post("", response_model=MachineResponse, status_code=201)
def create_machine(data: MachineCreate, db: Session = Depends(get_db)) -> Machine:
    """Create a new machine."""
    slug = data.slug or slugify(data.name)

    # Check for duplicate slug
    existing = db.execute(select(Machine).where(Machine.slug == slug)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail=f"Machine with slug '{slug}' already exists")

    machine = Machine(
        name=data.name,
        slug=slug,
        description=data.description,
        nozzle_diameter=data.nozzle_diameter,
    )
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


@router.get("/{machine_id}", response_model=MachineResponse)
def get_machine(machine_id: int, db: Session = Depends(get_db)) -> Machine:
    """Get a machine by ID."""
    machine = db.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine


@router.put("/{machine_id}", response_model=MachineResponse)
def update_machine(
    machine_id: int, data: MachineUpdate, db: Session = Depends(get_db)
) -> Machine:
    """Update a machine."""
    machine = db.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    if data.name is not None:
        machine.name = data.name
    if data.slug is not None:
        # Check for duplicate slug
        existing = db.execute(
            select(Machine).where(Machine.slug == data.slug, Machine.id != machine_id)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=400, detail=f"Machine with slug '{data.slug}' already exists"
            )
        machine.slug = data.slug
    if data.description is not None:
        machine.description = data.description
    if data.nozzle_diameter is not None:
        machine.nozzle_diameter = data.nozzle_diameter

    db.commit()
    db.refresh(machine)
    return machine


@router.delete("/{machine_id}", status_code=204)
def delete_machine(machine_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a machine."""
    machine = db.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    db.delete(machine)
    db.commit()
