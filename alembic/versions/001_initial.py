"""Initial migration - create all tables.

Revision ID: 001
Revises:
Create Date: 2025-01-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create machines table
    op.create_table(
        "machines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("nozzle_diameter", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    # Create plates table
    op.create_table(
        "plates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    # Create filaments table
    op.create_table(
        "filaments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("spoolman_filament_id", sa.Integer(), nullable=True),
        sa.Column("vendor", sa.String(length=255), nullable=False),
        sa.Column("material", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("color_name", sa.String(length=100), nullable=True),
        sa.Column("color_hex", sa.String(length=7), nullable=True),
        sa.Column("density", sa.Float(), nullable=True),
        sa.Column("diameter", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create profiles table
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filament_id", sa.Integer(), nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("plate_id", sa.Integer(), nullable=False),
        # Temperature settings
        sa.Column("nozzle_temp", sa.Integer(), nullable=False),
        sa.Column("nozzle_temp_first_layer", sa.Integer(), nullable=True),
        sa.Column("bed_temp", sa.Integer(), nullable=False),
        sa.Column("bed_temp_first_layer", sa.Integer(), nullable=True),
        sa.Column("chamber_temp", sa.Integer(), nullable=True),
        # Flow and extrusion
        sa.Column("flow_ratio", sa.Float(), nullable=True),
        sa.Column("pressure_advance", sa.Float(), nullable=True),
        sa.Column("max_volumetric_speed", sa.Float(), nullable=True),
        # Retraction
        sa.Column("retraction_length", sa.Float(), nullable=True),
        sa.Column("retraction_speed", sa.Float(), nullable=True),
        # Speeds
        sa.Column("print_speed", sa.Float(), nullable=True),
        sa.Column("first_layer_speed", sa.Float(), nullable=True),
        sa.Column("outer_wall_speed", sa.Float(), nullable=True),
        sa.Column("inner_wall_speed", sa.Float(), nullable=True),
        sa.Column("infill_speed", sa.Float(), nullable=True),
        sa.Column("travel_speed", sa.Float(), nullable=True),
        # Cooling
        sa.Column("fan_min_speed", sa.Integer(), nullable=True),
        sa.Column("fan_max_speed", sa.Integer(), nullable=True),
        sa.Column("disable_fan_first_layers", sa.Integer(), nullable=True),
        # Metadata
        sa.Column("is_default", sa.Boolean(), nullable=True),
        sa.Column("notes", sa.String(length=2000), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("source_profile", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["filament_id"], ["filaments.id"]),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.id"]),
        sa.ForeignKeyConstraint(["plate_id"], ["plates.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("filament_id", "machine_id", "plate_id", name="uq_profile_combination"),
    )


def downgrade() -> None:
    op.drop_table("profiles")
    op.drop_table("filaments")
    op.drop_table("plates")
    op.drop_table("machines")
