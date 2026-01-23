"""Machine schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MachineBase(BaseModel):
    """Base machine schema."""

    name: str
    description: str | None = None
    nozzle_diameter: float = 0.4


class MachineCreate(MachineBase):
    """Schema for creating a machine."""

    slug: str | None = None  # Will be auto-generated if not provided


class MachineUpdate(BaseModel):
    """Schema for updating a machine."""

    name: str | None = None
    slug: str | None = None
    description: str | None = None
    nozzle_diameter: float | None = None


class MachineResponse(MachineBase):
    """Schema for machine response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
