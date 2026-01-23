"""Machine model - represents a specific printer."""

from typing import TYPE_CHECKING

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from filamentprofiles.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from filamentprofiles.models.profile import Profile


class Machine(Base, TimestampMixin):
    """A 3D printer machine."""

    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    nozzle_diameter: Mapped[float] = mapped_column(Float, default=0.4)

    # Relationships
    profiles: Mapped[list["Profile"]] = relationship(back_populates="machine")
