"""Plate model - represents a build plate type."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from filamentprofiles.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from filamentprofiles.models.profile import Profile


class Plate(Base, TimestampMixin):
    """A build plate type."""

    __tablename__ = "plates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))

    # Relationships
    profiles: Mapped[list["Profile"]] = relationship(back_populates="plate")
