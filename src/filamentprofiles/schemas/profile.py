"""Profile schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from filamentprofiles.schemas.filament import FilamentResponse
from filamentprofiles.schemas.machine import MachineResponse
from filamentprofiles.schemas.plate import PlateResponse


class ProfileBase(BaseModel):
    """Base profile schema."""

    # Temperature settings
    nozzle_temp: int
    nozzle_temp_first_layer: int | None = None
    bed_temp: int
    bed_temp_first_layer: int | None = None
    chamber_temp: int | None = None

    # Flow and extrusion
    flow_ratio: float = 1.0
    pressure_advance: float | None = None
    max_volumetric_speed: float | None = None

    # Retraction
    retraction_length: float | None = None
    retraction_speed: float | None = None

    # Speeds
    print_speed: float | None = None
    first_layer_speed: float | None = None
    outer_wall_speed: float | None = None
    inner_wall_speed: float | None = None
    infill_speed: float | None = None
    travel_speed: float | None = None

    # Cooling
    fan_min_speed: int | None = None
    fan_max_speed: int | None = None
    disable_fan_first_layers: int | None = None

    # Metadata
    is_default: bool = False
    notes: str | None = None
    source: str | None = None
    source_profile: str | None = None


class ProfileCreate(ProfileBase):
    """Schema for creating a profile."""

    filament_id: int
    machine_id: int
    plate_id: int


class ProfileUpdate(BaseModel):
    """Schema for updating a profile."""

    # Temperature settings
    nozzle_temp: int | None = None
    nozzle_temp_first_layer: int | None = None
    bed_temp: int | None = None
    bed_temp_first_layer: int | None = None
    chamber_temp: int | None = None

    # Flow and extrusion
    flow_ratio: float | None = None
    pressure_advance: float | None = None
    max_volumetric_speed: float | None = None

    # Retraction
    retraction_length: float | None = None
    retraction_speed: float | None = None

    # Speeds
    print_speed: float | None = None
    first_layer_speed: float | None = None
    outer_wall_speed: float | None = None
    inner_wall_speed: float | None = None
    infill_speed: float | None = None
    travel_speed: float | None = None

    # Cooling
    fan_min_speed: int | None = None
    fan_max_speed: int | None = None
    disable_fan_first_layers: int | None = None

    # Metadata
    is_default: bool | None = None
    notes: str | None = None


class ProfileResponse(ProfileBase):
    """Schema for profile response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filament_id: int
    machine_id: int
    plate_id: int
    created_at: datetime
    updated_at: datetime


class ProfileDetailResponse(ProfileResponse):
    """Schema for profile response with related entities."""

    filament: FilamentResponse
    machine: MachineResponse
    plate: PlateResponse


class ProfileClone(BaseModel):
    """Schema for cloning a profile to a new machine/plate."""

    machine_id: int | None = None
    plate_id: int | None = None
