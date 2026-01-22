"""Plate schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlateBase(BaseModel):
    """Base plate schema."""

    name: str
    description: str | None = None


class PlateCreate(PlateBase):
    """Schema for creating a plate."""

    slug: str | None = None  # Will be auto-generated if not provided


class PlateUpdate(BaseModel):
    """Schema for updating a plate."""

    name: str | None = None
    slug: str | None = None
    description: str | None = None


class PlateResponse(PlateBase):
    """Schema for plate response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
