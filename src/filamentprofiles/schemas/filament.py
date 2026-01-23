"""Filament schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FilamentBase(BaseModel):
    """Base filament schema."""

    vendor: str
    material: str
    name: str
    color_name: str | None = None
    color_hex: str | None = None
    density: float | None = None
    diameter: float = 1.75


class FilamentCreate(FilamentBase):
    """Schema for creating a filament."""

    spoolman_filament_id: int | None = None


class FilamentUpdate(BaseModel):
    """Schema for updating a filament."""

    vendor: str | None = None
    material: str | None = None
    name: str | None = None
    color_name: str | None = None
    color_hex: str | None = None
    density: float | None = None
    diameter: float | None = None
    spoolman_filament_id: int | None = None


class FilamentResponse(FilamentBase):
    """Schema for filament response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    spoolman_filament_id: int | None
    created_at: datetime
    updated_at: datetime
