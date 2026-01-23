"""Filament model - reference to a Spoolman filament with cached data."""

from typing import TYPE_CHECKING

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from filamentprofiles.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from filamentprofiles.models.profile import Profile


class Filament(Base, TimestampMixin):
    """A filament type, optionally linked to Spoolman."""

    __tablename__ = "filaments"

    id: Mapped[int] = mapped_column(primary_key=True)
    spoolman_filament_id: Mapped[int | None] = mapped_column(Integer)

    # Filament info (cached from Spoolman or manually entered)
    vendor: Mapped[str] = mapped_column(String(255), nullable=False)
    material: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    color_name: Mapped[str | None] = mapped_column(String(100))
    color_hex: Mapped[str | None] = mapped_column(String(7))  # e.g., "#E8E0D5"
    density: Mapped[float | None] = mapped_column(Float)  # g/cm³
    diameter: Mapped[float] = mapped_column(Float, default=1.75)

    # Relationships
    profiles: Mapped[list["Profile"]] = relationship(back_populates="filament")
