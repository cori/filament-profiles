"""Profile model - the core entity for print settings."""

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from filamentprofiles.models.base import Base, TimestampMixin
from filamentprofiles.models.filament import Filament
from filamentprofiles.models.machine import Machine
from filamentprofiles.models.plate import Plate


class Profile(Base, TimestampMixin):
    """Print settings for a filament + machine + plate combination."""

    __tablename__ = "profiles"
    __table_args__ = (
        UniqueConstraint("filament_id", "machine_id", "plate_id", name="uq_profile_combination"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    filament_id: Mapped[int] = mapped_column(ForeignKey("filaments.id"), nullable=False)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id"), nullable=False)
    plate_id: Mapped[int] = mapped_column(ForeignKey("plates.id"), nullable=False)

    # Temperature settings
    nozzle_temp: Mapped[int] = mapped_column(Integer, nullable=False)
    nozzle_temp_first_layer: Mapped[int | None] = mapped_column(Integer)
    bed_temp: Mapped[int] = mapped_column(Integer, nullable=False)
    bed_temp_first_layer: Mapped[int | None] = mapped_column(Integer)
    chamber_temp: Mapped[int | None] = mapped_column(Integer)

    # Flow and extrusion
    flow_ratio: Mapped[float] = mapped_column(Float, default=1.0)
    pressure_advance: Mapped[float | None] = mapped_column(Float)
    max_volumetric_speed: Mapped[float | None] = mapped_column(Float)

    # Retraction
    retraction_length: Mapped[float | None] = mapped_column(Float)
    retraction_speed: Mapped[float | None] = mapped_column(Float)

    # Speeds (optional overrides)
    print_speed: Mapped[float | None] = mapped_column(Float)
    first_layer_speed: Mapped[float | None] = mapped_column(Float)
    outer_wall_speed: Mapped[float | None] = mapped_column(Float)
    inner_wall_speed: Mapped[float | None] = mapped_column(Float)
    infill_speed: Mapped[float | None] = mapped_column(Float)
    travel_speed: Mapped[float | None] = mapped_column(Float)

    # Cooling
    fan_min_speed: Mapped[int | None] = mapped_column(Integer)
    fan_max_speed: Mapped[int | None] = mapped_column(Integer)
    disable_fan_first_layers: Mapped[int | None] = mapped_column(Integer)

    # Metadata
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(String(2000))
    source: Mapped[str | None] = mapped_column(String(50))  # "manual", "spoolmandb", "imported"
    source_profile: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    filament: Mapped["Filament"] = relationship(back_populates="profiles")
    machine: Mapped["Machine"] = relationship(back_populates="profiles")
    plate: Mapped["Plate"] = relationship(back_populates="profiles")
